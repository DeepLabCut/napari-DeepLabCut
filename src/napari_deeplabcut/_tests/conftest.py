import cv2
import numpy as np
import pandas as pd
import pytest
from napari_deeplabcut import keypoints, _writer, _widgets
from skimage.io import imsave


@pytest.fixture
def fake_keypoints():
    n_rows = 10
    n_animals = 2
    n_kpts = 3
    data = np.random.rand(n_rows, n_animals * n_kpts * 2)
    cols = pd.MultiIndex.from_product([
        ["me"],
        [f"animal_{i}" for i in range(n_animals)],
        [f"kpt_{i}" for i in range(n_kpts)],
        ["x", "y"]
    ], names=["scorer", "individuals", "bodyparts", "coords"])
    df = pd.DataFrame(data, columns=cols, index=range(n_rows))
    return df


@pytest.fixture
def points(tmp_path_factory, make_napari_viewer, fake_keypoints):
    output_path = str(tmp_path_factory.mktemp("folder") / "fake_data.h5")
    fake_keypoints.to_hdf(output_path, key="data")
    viewer = make_napari_viewer()
    layer = viewer.open(output_path, plugin="napari-deeplabcut")[0]
    layer._viewer = viewer  # Hold a reference to the viewer for the `store`
    return layer


@pytest.fixture
def fake_image():
    return (np.random.rand(10, 10) * 255).astype(np.uint8)


@pytest.fixture
def images(tmp_path_factory, make_napari_viewer, fake_image):
    output_path = str(tmp_path_factory.mktemp("folder") / "img.png")
    imsave(output_path, fake_image)
    viewer = make_napari_viewer()
    layer = viewer.open(output_path, plugin="napari-deeplabcut")[0]
    return layer


@pytest.fixture
def store(points):
    return keypoints.KeypointStore(points._viewer, points)


@pytest.fixture
def controls(make_napari_viewer):
    viewer = make_napari_viewer()
    return _widgets.KeypointControls(viewer)


@pytest.fixture(scope="session")
def config_path(tmp_path_factory):
    cfg = {
        "scorer": "me",
        "bodyparts": list("abc"),
        "dotsize": 0,
        "pcutoff": 0,
        "colormap": "viridis",
        "video_sets": {
            "fake_video": [],
        }
    }
    path = str(tmp_path_factory.mktemp("configs") / "config.yaml")
    _writer._write_config(
        path, params=cfg,
    )
    return path


@pytest.fixture(scope="session")
def video_path(tmp_path_factory):
    output_path = str(tmp_path_factory.mktemp("data") / "fake_video.avi")
    h = w = 50
    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*'MJPG'),
        2,
        (w, h),
    )
    for _ in range(5):
        frame = np.random.randint(0, 255, (h, w, 3)).astype(np.uint8)
        writer.write(frame)
    writer.release()
    return output_path
