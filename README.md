# ZED Camera Real-Time 3D Point Cloud Visualization with Open3D

This project demonstrates how to capture real-time 3D point cloud data from a ZED camera using the ZED SDK and visualize it with Open3D. The application allows users to interactively view the point cloud and save snapshots in `.ply` format.

## Features

- **Real-Time Point Cloud Capture:** Streams 3D data from the ZED camera in real-time.
- **Open3D Visualization:** Displays the captured point cloud using Open3D.
- **Interactive Controls:**
  - Press `Space` to save the current point cloud as a `.ply` file.
  - Press `Esc` to exit the application.

## Getting Started

### Prerequisites

To run this project, you need the following:

- **ZED SDK:** Ensure that the ZED SDK is installed and your ZED camera is connected.
- **Python 3.6+**

### Installation

1. **Install the ZED SDK:**
   Follow the instructions on the [ZED SDK installation page](https://www.stereolabs.com/docs/installation/).

2. **Clone the Repository:**
   If you haven't already, clone this repository to your local machine:
   ```bash
   git clone https://github.com/JackmanYuan/ZED_point_cloud_recorder.git
   cd ZED_point_cloud_recorder
   ```

3. **Install Python Dependencies:**
   The required Python packages are listed in the `requirements.txt` file. Install them using the following command:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To run the application, simply execute the Python script:

```bash
python zed_point_cloud_recorder.py
```

Once the application starts, you'll see a visualization window displaying the 3D point cloud captured by the ZED camera.

### Keyboard Controls

- **Space:** Save the current point cloud as a `.ply` file.
- **Esc:** Exit the application.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **ZED SDK:** For providing the tools to capture 3D data.
- **Open3D:** For making 3D visualization in Python simple and powerful.