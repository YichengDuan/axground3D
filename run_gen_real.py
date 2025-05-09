from config_util import (
    MP3D_DATASET_PATH,
    MP3D_DATASET_SCENE_IDS_LIST,
    NUM_OF_NODES_PRE_SCENE,
    ACTION_CHUNK,
)

from sim_connect.hb import init_simulator, create_viewer
import os
import magnum as mn
import numpy as np
from joblib import Parallel, delayed
from PIL import Image


def random_sample(pathfinder, num_nodes: int):
    samples = []
    attempts = 0
    max_attempts = num_nodes * 10  # Avoid infinite loops
    while len(samples) < num_nodes and attempts < max_attempts:
        pt = pathfinder.get_random_navigable_point()
        if not any(np.allclose(pt, s['point'], atol=1e-3) for s in samples):  # avoid near-duplicates
            sample = {'point': pt, 'radius': None}
            samples.append(sample)
        attempts += 1
    return samples

def run_gen_real(scene_id:str):
    scene_path = os.path.join(MP3D_DATASET_PATH, scene_id, f"{scene_id}.glb")
    sim = init_simulator(scene_path, is_physics=True)
    viewer = create_viewer(scene_path)
    pathfinder = sim.pathfinder

    samples = random_sample(pathfinder, NUM_OF_NODES_PRE_SCENE)
    for ids, s in enumerate(samples):
        pos = s["point"]
        if isinstance(pos, str):
            pos = list(map(float, pos.split(",")))
        vec = mn.Vector3(*pos)
        viewer.transit_to_goal(vec)
        file_name = os.path.join("./frames/state_base", f"{scene_id}_s{ids}_step_base.png")
        state_img = viewer.save_viewpoint_image(file_name)

        ply_file_name = os.path.join(
            "./data", f"{scene_id}_s{ids}_base.ply"
        )

        for _id, action in enumerate(ACTION_CHUNK):
            if _id != 2 and _id != 3:
        
                viewer.move_and_look(action["name"], action["repeat"])
                file_name = os.path.join(
                    "./frames/real", f"{scene_id}_s{ids}_step{_id}.png"
                )
                viewer.save_viewpoint_image(file_name)
        
            else:
                viewer.move_and_look(action["name"], action["repeat"])

    sim.close()
    viewer.close()



if __name__ == "__main__":
    results = Parallel(n_jobs=2)(
        # stack the scene into path
        delayed(run_gen_real)(
            scene_id=scene_id,
        )
        for scene_id in MP3D_DATASET_SCENE_IDS_LIST
    )