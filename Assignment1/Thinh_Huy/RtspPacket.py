SETUP = 0
PLAY = 1
PAUSE = 2
TEARDOWN = 3
DESCRIBE = 4
FORWARD5SECONDS = 5
BACKWARD5SECONDS = 6

class RtspPacket:

    def __init__(self, request_type, video_file_path, sequence_number, dst_port=None, session_id=None):
        self.rtsp_version = "RTSP/1.0"
        self.request_type = request_type
        self.video_file_path = video_file_path
        self.sequence_number = sequence_number
        self.dst_port = dst_port
        self.session_id = session_id

    def generate(self):
        if self.request_type == SETUP:
            self.client_rtp_port = self.dst_port
            request_line = [
                f"SETUP {self.video_file_path} {self.rtsp_version}",
                f"CSeq: {self.sequence_number}",
                f"Transport: RTP/UDP; client_port= {self.client_rtp_port}"
            ]
            request = '\n'.join(request_line) + '\n'
            return request.encode()

        if self.request_type == PLAY:
            request_line = [
                f"PLAY {self.video_file_path} {self.rtsp_version}",
                f"CSeq: {self.sequence_number}",
                f"Session: {self.session_id}"
            ]
            request = '\n'.join(request_line) + '\n'
            return request.encode()

        if self.request_type == PAUSE:
            request_line = [
                f"PAUSE {self.video_file_path} {self.rtsp_version}",
                f"CSeq: {self.sequence_number}",
                f"Session: {self.session_id}"
            ]
            request = '\n'.join(request_line) + '\n'
            return request.encode()

        if self.request_type == TEARDOWN:
            request_line = [
                f"TEARDOWN {self.video_file_path} {self.rtsp_version}",
                f"CSeq: {self.sequence_number}",
                f"Session: {self.session_id}"
            ]
            request = '\n'.join(request_line) + '\n'
            return request.encode()

        if self.request_type == DESCRIBE:
            request_line = [
                f"DESCRIBE {self.video_file_path} {self.rtsp_version}",
                f"CSeq: {self.sequence_number}",
                f"Session: {self.session_id}"
            ]
            request = '\n'.join(request_line) + '\n'
            return request.encode()

        if self.request_type == FORWARD5SECONDS:
            request_line = [
                f"FORWARD5SECONDS {self.video_file_path} {self.rtsp_version}",
                f"CSeq: {self.sequence_number}",
                f"Session: {self.session_id}"
            ]
            request = '\n'.join(request_line) + '\n'
            return request.encode()

        if self.request_type == BACKWARD5SECONDS:
            request_line = [
                f"BACKWARD5SECONDS {self.video_file_path} {self.rtsp_version}",
                f"CSeq: {self.sequence_number}",
                f"Session: {self.session_id}"
            ]
            request = '\n'.join(request_line) + '\n'
            return request.encode()
