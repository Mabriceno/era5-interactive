# map_plot.py
import numpy as np
import xarray as xr
import plotly.graph_objects as go
from typing import Dict, Literal, Optional

# --- NEW ---
import cartopy.crs as ccrs
from functools import lru_cache

# --------------------------------------------------------------------------- #
#                              helpers                                        #
# --------------------------------------------------------------------------- #
@lru_cache
def _cartopy_proj(name: str) -> ccrs.Projection:
    """Devuelve la proyección cartopy correspondiente al string de Plotly."""
    name = name.lower()
    if name in ("robinson", "robin"):
        return ccrs.Robinson()
    if name in ("mercator", "merc"):
        return ccrs.Mercator()
    if name in ("orthographic", "ortho"):
        return ccrs.Orthographic(central_longitude=0)
    if name in ("mollweide", "moll"):
        return ccrs.Mollweide()
    # fallback: lat/lon (Plotly = equirectangular)
    return ccrs.PlateCarree()

def _to_proj_xy(lon_2d: np.ndarray, lat_2d: np.ndarray,
                target: ccrs.Projection) -> tuple[np.ndarray, np.ndarray]:
    """
    Transforma lon/lat (º) → x/y (m) en la proyección destino (Cartopy).
    """
    src = ccrs.PlateCarree()
    pts = target.transform_points(src, lon_2d, lat_2d)
    return pts[..., 0], pts[..., 1]        # x, y


# --------------------------------------------------------------------------- #
#                           main plotting func                                #
# --------------------------------------------------------------------------- #
def plot_spatial_map(
        data: xr.DataArray,
        title: str = "Spatial Map",
        color_scale: str = "Viridis",
        projection: str = "robinson",
        *,
        max_cells: int = 2_000_00,              # ≈ 500×400
        coarsen_factor: Optional[int] = None,
        method: Literal["auto", "contour", "heatmap"] = "heatmap",
        levels: int = 10,
) -> go.Figure:
    """
    Interactivo + rápido; ahora soporta proyecciones Cartopy.
    """
    # ------------ 1. Detectar coords ----------------------------------------
    lon_name = next(n for n in ("lon", "longitude", "x") if n in data.coords)
    lat_name = next(n for n in ("lat", "latitude", "y") if n in data.coords)

    # ------------ 2. Down‑sample opcional -----------------------------------
    n_lon, n_lat = data[lon_name].size, data[lat_name].size
    total = n_lon * n_lat

    if coarsen_factor is None and total > max_cells:
        coarsen_factor = int(np.ceil(np.sqrt(total / max_cells)))
    if coarsen_factor and coarsen_factor > 1:
        data = (
            data.coarsen({lat_name: coarsen_factor, lon_name: coarsen_factor},
                         boundary="trim")
            .mean()
        )
        n_lon, n_lat = data[lon_name].size, data[lat_name].size
        total = n_lon * n_lat

    # ------------ 3. Elegir método visual -----------------------------------
    if method == "auto":
        method = "contour" if total <= max_cells else "heatmap"

    lon = data[lon_name].values
    lat = data[lat_name].values
    z   = data.values

    fig = go.Figure()

    # ----------------------------------------------------------------------- #
    #            CASO A: proyección “plana” → lo de siempre                   #
    # ----------------------------------------------------------------------- #
    if projection.lower() in ("equirectangular", "platecarree", "latlon", "geo"):
        if method == "contour":
            fig.add_trace(
                go.Contour(
                    z=z, x=lon, y=lat,
                    colorscale=color_scale,
                    ncontours=levels,
                    colorbar=dict(title=data.name or "value"),
                    contours=dict(showlines=False),
                    hovertemplate=(
                        f"{lat_name}: %{{y:.2f}}<br>"
                        f"{lon_name}: %{{x:.2f}}<br>"
                        f"%{{z:.3g}}<extra></extra>"
                    ),
                )
            )
        else:  # heatmap cartesiano
            Heat = go.Heatmapgl if total > 50_000 else go.Heatmap
            fig.add_trace(
                Heat(
                    z=z, x=lon, y=lat,
                    colorscale=color_scale,
                    colorbar=dict(title=data.name or "value"),
                    zsmooth="best",
                    hovertemplate=(
                        f"{lat_name}: %{{y:.2f}}<br>"
                        f"{lon_name}: %{{x:.2f}}<br>"
                        f"%{{z:.3g}}<extra></extra>"
                    ),
                )
            )
        fig.update_yaxes(scaleanchor="x")  # mantiene aspect ratio
    # ----------------------------------------------------------------------- #
    #           CASO B: proyección Cartopy  → ScatterGL                       #
    # ----------------------------------------------------------------------- #
    else:
        proj = _cartopy_proj(projection)
        Lon2d, Lat2d = np.meshgrid(lon, lat)
        x, y = _to_proj_xy(Lon2d, Lat2d, proj)

        # aplanar para ScatterGL
        x_f, y_f, z_f = x.ravel(), y.ravel(), z.ravel()

        fig.add_trace(
            go.Scattergl(
                x=x_f, y=y_f,
                mode="markers",
                marker=dict(
                    symbol="square",
                    size=3,                # ≈ pixel
                    colorscale=color_scale,
                    color=z_f,
                    colorbar=dict(title=data.name or "value"),
                    showscale=True,
                ),
                hovertemplate=(
                    f"{lat_name}: %{{customdata[0]:.2f}}<br>"
                    f"{lon_name}: %{{customdata[1]:.2f}}<br>"
                    f"%{{marker.color:.3g}}<extra></extra>"
                ),
                customdata=np.stack([Lat2d.ravel(), Lon2d.ravel()], axis=-1),
            )
        )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

    # ------------ 4. Layout --------------------------------------------------
    fig.update_layout(
        title=title,
        template="plotly_white",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig