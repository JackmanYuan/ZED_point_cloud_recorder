"""
    This sample demonstrates how to get a realtime 3D point cloud   
    with the ZED SDK and visualize + capture the result with Open3D.    
"""

import ctypes
import pyzed.sl as sl
import open3d as o3d
import numpy as np
from datetime import datetime


if __name__ == "__main__":
    # Initialize zed parameters
    init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
                             depth_mode=sl.DEPTH_MODE.ULTRA,
                             coordinate_units=sl.UNIT.METER)
    zed = sl.Camera()
    status = zed.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print(repr(status))
        exit()

    res = sl.Resolution()
    res.width = 720
    res.height = 404

    camera_model = zed.get_camera_information().camera_model

    # Initialize zed sl Mat object to save pointcloud
    point_cloud = sl.Mat(res.width, res.height, sl.MAT_TYPE.F32_C4, sl.MEM.CPU)

    # Initialize zed runtime parameter
    runtime_parameter = sl.RuntimeParameters()

    '''
    Create Open3D visulizer
    '''
    # Initialize window and visualize settings
    window_height = 600
    window_width = 600
    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window(window_name="Pointcloud",
                      height=window_height, width=window_width)

    # Get render object to set background color
    opt = vis.get_render_option()
    # I prefer a dark grey backgroud color
    opt.background_color = np.asarray([0.2, 0.2, 0.2])
    # How big you want for each point in the poit cloud
    opt.point_size = 0.5

    # Initialize a point cloud object, we will later update this object with zed sensor measurement
    sensor_data = o3d.geometry.PointCloud()
    sensor_coor = [[0, 0, 0]]
    sensor_data.points = o3d.utility.Vector3dVector(np.array(sensor_coor))
    # Don't forget to add it into your visualizer
    vis.add_geometry(sensor_data)

    # Initialize a coordinate frame object so we can have a better idea of the zed camera's pose
    axis_pcd = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[
                                                                 0, 0, 0])
    # Don't forget to add it into your visualizer as well!
    vis.add_geometry(axis_pcd)

    # Set viewer control, so you can adjust hoe you want to view the visualizer.
    ctr = vis.get_view_control()
    ctr.rotate(0, 1100)
    ctr.translate(250, 200)
    ctr.set_zoom(5)
    ctr.set_constant_z_far(20)

    vis.poll_events()
    vis.update_renderer()

    # Tricky part alert!
    # Here we initialize an np array and pointer.
    # So later we can get ZED 3D point cloud measurement and save to this np array.
    sensor_points = np.zeros((res.height*res.width, 4), dtype=np.float32)
    ptr_sensor_points = sensor_points.ctypes.data_as(
        ctypes.POINTER(ctypes.c_float))
    buffer_size = res.width * res.height * ctypes.sizeof(ctypes.c_float) * 4

    # These flags are used to control when we want to save 1 point cloud or exit this sample.
    loop_flag = True
    save_flag = False

    # This function will help us get the rgb data we need for updating open3d point cloud object
    def decode_float_to_rgba(color_float):
        color_data = color_float.copy()
        color_data.dtype = np.uint32
        a = np.asarray((color_data >> 24) & 0xFF, dtype=np.uint8)
        g = np.asarray((color_data >> 16) & 0xFF, dtype=np.uint8)
        b = np.asarray((color_data >> 8) & 0xFF, dtype=np.uint8)
        r = np.asarray(color_data & 0xFF, dtype=np.uint8)

        rgb = np.zeros((len(color_data), 3), dtype=np.float64)
        rgb[:, 0] = r[:, 0]/255
        rgb[:, 1] = b[:, 0]/255
        rgb[:, 2] = g[:, 0]/255

        return rgb

    # Set keyboard controls
    def key_save(vis):
        global save_flag
        save_flag = True

    def key_exit(vis):
        global loop_flag
        loop_flag = False
        print('!!!!!Exit!!!!!')

    vis.register_key_callback(32, key_save)
    vis.register_key_callback(256, key_exit)

    """
    Finally! We are going to start the loop and:
    1. ZED mini start getting data
    2. We take the ZED 3D point cloud data and save it to a .ply file
    """
    print('Running point cloud collecting tool!\n1. Press Space to save 1 frame of point cloud. \n2. Press Esc to exit')
    while loop_flag:
        if save_flag == True:
            print("Collecting point cloud...")
            date_time = datetime.now()
            date_time_str = date_time.strftime('%Y%m%d_%H%M%S')
            o3d.io.write_point_cloud(
                './zed_depth_' + date_time_str + '.ply', sensor_data, write_ascii=True)
            print('Done! zed_depth_" + date_time_str + ".ply is saved')
            save_flag = False

        else:
            if zed.grab(runtime_parameter) == sl.ERROR_CODE.SUCCESS:
                # This is the function from ZED SDK that will get you the 3D point cloud!
                zed.retrieve_measure(
                    point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, res)

                # Tricky part is here! To get the point cloud data with better update rate, here we
                # "redirect" ZED sensor pointer to np array pointer, get the point cloud data and save it as np array
                ctypes.memmove(ptr_sensor_points, ctypes.c_void_p(
                    point_cloud.get_pointer()), buffer_size)
                copy_sensor_points = sensor_points

                # Filter out nan and inf
                copy_sensor_points = copy_sensor_points[~np.isnan(
                    copy_sensor_points[:, 0:3]).any(axis=1), :]
                copy_sensor_points = copy_sensor_points[~np.isinf(
                    copy_sensor_points[:, 0:3]).any(axis=1), :]

                # Get the points' coordinates and colors
                sensor_coor = copy_sensor_points[:, 0:3]
                sensor_color = copy_sensor_points[:, 3:]
                sensor_color = decode_float_to_rgba(sensor_color)

                # Update the open3d point cloud object
                sensor_data.points = o3d.utility.Vector3dVector(sensor_coor)
                sensor_data.colors = o3d.utility.Vector3dVector(sensor_color)

                # Update visualizer to display the rgb point cloud!
                vis.update_geometry(sensor_data)
                vis.update_geometry(axis_pcd)
                vis.poll_events()
                vis.update_renderer()

    vis.destroy_window()
    zed.close()
