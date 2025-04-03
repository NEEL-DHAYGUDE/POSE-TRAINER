# Pose Trainer - IoT-Based Real-Time Pose Recognition System

## Overview
Pose Trainer is an IoT-based real-time pose recognition system designed to help users practice and test poses using a webcam. It leverages MediaPipe for pose detection, Firebase for cloud storage, and WebSockets for real-time communication with external devices.

## Features
- **Pose Detection**: Uses MediaPipe to detect human poses and compare them with stored poses.
- **Firebase Integration**: Stores saved poses and leaderboard scores in Firebase Realtime Database.
- **WebSocket Communication**: Enables real-time messaging between the system and external devices.
- **User and Coach Login System**: Separate functionalities for users and coaches.
- **Leaderboard**: Stores and displays user scores based on pose matching accuracy.

## Installation
### Prerequisites
- Python 3.x
- Firebase Admin SDK JSON file
- Required Python Libraries:
  ```bash
  pip install opencv-python mediapipe numpy firebase-admin tkinter websockets pillow
  ```

## Usage
1. **Run the program**
   ```bash
   python pose_trainer.py
   ```
2. **Login as Coach or User**:
   - **Coach**: Can add poses, view stored poses, and see leaderboard scores.
   - **User**: Can practice, test poses, and view leaderboard scores.
3. **WebSocket Communication**:
   - The coach can send real-time messages to connected devices.
4. **Pose Practice & Testing**:
   - Users can practice saved poses and get feedback on their accuracy.
   - Users can take a test where a random pose is assigned for evaluation.

## File Structure
```
Pose Trainer/
│-- pose_trainer.py  # Main Python script
│-- poses/           # Directory storing pose JSON files and images
│-- leaderboard.json # Local leaderboard storage
│-- logo.png         # App logo (if available)
```

## Technologies Used
- **MediaPipe**: Pose detection.
- **OpenCV**: Image processing.
- **Firebase**: Cloud storage for poses and scores.
- **WebSockets**: Real-time communication.
- **Tkinter**: GUI for user interaction.

## Future Improvements
- Mobile application integration for better accessibility.
- More advanced pose comparison algorithms.
- Real-time feedback using AI-based pose correction.


## Author
Developed by Neel Dhaygude.

