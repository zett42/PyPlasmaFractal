import moderngl
import numpy as np
import imageio

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
        self.file_path = file_path
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_count = 0

        self.writer = imageio.get_writer(self.file_path, fps=self.fps, codec='libx264', quality=10)



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
        if self.writer is None:
            raise ValueError("Video recording has not been started.")

        if texture.width != self.width or texture.height != self.height:
            raise ValueError(f"Texture dimensions do not match size specified at begin of recording: {self.width}x{self.height}, "
                             f"got {texture.width}x{texture.height}")

        texture.use()
        data = texture.read()
        numpy_dtype = np.dtype(texture.dtype)  # Assuming texture.dtype is directly usable
        
        image = np.frombuffer(data, dtype=numpy_dtype).reshape(self.height, self.width, 4)
        image_rgb = image[:, :, :3]  # Assuming the texture includes an alpha channel
        image_uint8 = np.clip(image_rgb * 255, 0, 255).astype(np.uint8)
        self.writer.append_data(image_uint8)

        self.frame_count += 1


    def stop_recording(self):
        """
        Stops the video recording and finalizes the video file.

        Closes the video writer and ensures that all data is flushed and the file is
        properly finalized. This method should be called to properly close the video file
        after all frames have been captured.
        """
        if self.writer is not None:
            self.writer.close()
            self.writer = None
            self.frame_count = 0


    def __del__(self):
        """
        Ensures that resources are cleaned up when the VideoRecorder instance is destroyed.

        This destructor method calls stop_recording to ensure that the video writer is properly
        closed if it is still open, preventing data loss.
        """
        self.stop_recording()
