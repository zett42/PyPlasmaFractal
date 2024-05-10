import logging
import os
from typing import Tuple
import moderngl
import numpy as np
import imageio

class VideoRecorderException(Exception):
    """Custom exception class for VideoRecorder errors."""
    pass


class VideoRecorder:
    """
    A class to handle the recording of video files from rendered texture data in real-time applications.

    This class provides a flexible way to start, capture, and stop video recording of rendering outputs,
    managing both the initialization and the finalization of video files. It supports dynamic resolution changes,
    making it suitable for applications where the render window or output texture size may vary during runtime.
    
    The recorder utilizes `imageio` to handle the video file creation and data encoding, with configurable
    parameters for video quality and format.

    Attributes:
        file_path (str): File path where the video will be saved.
        fps (int): Frames per second of the video.
        codec (str): Codec used for encoding the video.
        writer (imageio.core.format.Writer): The video writer instance used for recording frames.
        width (int): The width of the video, set when recording starts.
        height (int): The height of the video, set when recording starts.

    Example:
        recorder = VideoRecorder('output.mp4', fps=20)
        recorder.start_recording(800, 600)
        while rendering:
            recorder.capture_frame(current_texture)
        recorder.stop_recording()
    """
    
    def __init__(self):
        """
        Initializes a new instance of the VideoRecorder.
        """        
        self.file_path = None
        self.width = None
        self.height = None
        self.fps = None
        self.codec = None
        self.writer = None
        self.frame_count = 0


    @property
    def is_recording(self) -> bool:
        """
        Checks if the video recorder is currently recording.

        Returns:
            bool: True if the recorder is currently recording, False otherwise.
        """
        return self.writer is not None
    
    @property
    def recording_time(self) -> float:
        """
        Returns the total recording time in seconds.

        Returns:
            float: The total recording time in seconds.
        """
        return self.frame_count / self.fps if self.fps else 0.0


    def start_recording(self, file_path: str, width: int, height: int, fps=60):
        """
        Starts the video recording by initializing the video writer with specified dimensions.

        Parameters:
            width (int): The width of the video frames.
            height (int): The height of the video frames.

        Raises:
            RuntimeError: If the video writer fails to initialize.

        Starts the video writer to allow frame capturing with the given dimensions. This
        method must be called before capturing any frames.
        """

        if self.is_recording:
            raise VideoRecorderException("Recording is already active.")

        if not file_path:
            raise VideoRecorderException("File path must not be empty.")

        if width <= 0 or height <= 0:
            raise VideoRecorderException(f"Invalid video dimensions ({width}x{height}) provided.")

        # Try to create an empty file to validate the file path
        try:
            with open(file_path, 'a') as f:
                pass
        except Exception as e:
            raise VideoRecorderException(f"Failed to validate file path '{file_path}': {e}") from e

        self.file_path = file_path
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_count = 0

        logging.debug(f"Starting video recording to '{file_path}' at {width}x{height} with {fps} FPS.")

        try:
            self.writer = imageio.get_writer(self.file_path, fps=self.fps, codec='libx264', quality=10)
        except Exception as e:
            raise VideoRecorderException("Failed to initialize video writer.") from e


    def capture_frame(self, texture: moderngl.Texture):
        """
        Captures a single frame from the provided texture and writes it to the video.

        Parameters:
            texture (Texture): The texture object from which the frame data is captured.

        Raises:
            ValueError: If recording has not started or if the texture dimensions do not match
                        the dimensions specified at the start of recording.

        This method reads pixel data from the specified texture, validates its dimensions,
        converts the data to the appropriate format, and appends it to the video stream.
        """
        if not self.is_recording:
            raise VideoRecorderException("Video recording has not been started.")

        try:
            texture.use()
            data = texture.read()
            numpy_dtype = np.dtype(texture.dtype)  # Assuming texture.dtype is directly usable
            
            image = np.frombuffer(data, dtype=numpy_dtype).reshape(self.height, self.width, 4)
            image_rgb = image[:, :, :3]  # Assuming the texture includes an alpha channel
            image_uint8 = np.clip(image_rgb * 255, 0, 255).astype(np.uint8)
            self.writer.append_data(image_uint8)

            self.frame_count += 1

        except Exception as e:
            try:
                self.writer.close()
            except Exception as e:
                # Log error message
                logging.error(f"Could not close the video writer during exception handling: {e}")

            self.writer = None
            raise VideoRecorderException("Failed to capture frame.") from e


    def stop_recording(self):
        """
        Stops the video recording and finalizes the video file.

        Closes the video writer and ensures that all data is flushed and the file is
        properly finalized. This method should be called to properly close the video file
        after all frames have been captured.
        """
        if not self.is_recording:
            raise VideoRecorderException("No active recording to stop.")

        try:
            self.writer.close()
            logging.debug(f"Video recording stopped. {self.frame_count} frames captured.")

        except Exception as e:
            raise VideoRecorderException("Failed to finalize video file.") from e
        finally:
            self.writer = None


    def __del__(self):
        """
        Ensures that resources are cleaned up when the VideoRecorder instance is destroyed.
        This destructor method calls stop_recording to ensure that the video writer is properly
        closed if it is still open, preventing data loss.
        """
        if self.is_recording:
            try:
                self.stop_recording()
            except VideoRecorderException as e:
                # Log and suppress exceptions (best practice in __del__ methods to avoid exceptions during cleanup)
                logging.error(f"Failed to stop recording during object finalization: {e}")
            except Exception as e:
                # Log and suppress exceptions (best practice in __del__ methods to avoid exceptions during cleanup)
                logging.error(f"Unexpected error during object finalization: {e}")


    def get_aligned_dimensions(self, width: int, height: int) -> Tuple[int, int]:
        """
        Adjusts the width and height to meet alignment requirements for video encoding.

        Parameters:
            width (int): Original width of the video frame.
            height (int): Original height of the video frame.

        Returns:
            (int, int): Adjusted width and height that are aligned to meet codec requirements.
        """
        if width <= 0 or height <= 0:
            raise VideoRecorderException(f"Invalid dimensions ({width}x{height}) provided for alignment.")

        # Ensure dimensions are even for libx264 compatibility
        if width % 2 != 0:
            width += 1
        if height % 2 != 0:
            height += 1

        return width, height