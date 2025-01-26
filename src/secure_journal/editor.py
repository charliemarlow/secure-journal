import shutil
import subprocess
import time

ERROR_EMACS_NOT_FOUND = "Emacs not found in PATH"


class Editor:
    def __init__(self) -> None:
        """Initialize the Emacs editor."""
        emacsclient_path = shutil.which("emacsclient")
        emacs_path = shutil.which("emacs")
        if not emacsclient_path or not emacs_path:
            raise RuntimeError(ERROR_EMACS_NOT_FOUND)
        self.emacsclient_path = emacsclient_path
        self.emacs_path = emacs_path
        self._start_emacs_server()

    def _start_emacs_server(self) -> None:
        """Start Emacs server if not already running."""
        try:
            # Check if server is running
            subprocess.run(
                [self.emacsclient_path, "--eval", "t"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            # Start server if not running
            subprocess.Popen(
                [self.emacs_path, "--daemon"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Wait for server to start
            time.sleep(1)

    def open_buffer(self, initial_content: str | None) -> str:
        escaped_content = (
            initial_content.replace("\\", "\\\\").replace('"', '\\"')
            if initial_content
            else ""
        )
        get_buffer_cmd = f"""
          (progn
              (setq buf (generate-new-buffer "*journal*"))
              (with-current-buffer buf
                  (setq buffer-file-name nil)
                  (setq auto-save-default nil)
                  (setq make-backup-files nil)
                  (setq create-lockfiles nil)
                  (display-line-numbers-mode)
                  (insert "{escaped_content}")
                  (goto-char (point-min))
                  ;; Add word count in mode line with live updates
                  (setq mode-line-format
                      (list
                          " "
                          mode-line-buffer-identification
                          "   Words: "
                          '(:eval (number-to-string '
                          (count-words (point-min) (point-max))))
                      ))
                  ;; Force mode line update after any change
                  (add-hook 'after-change-functions
                      (lambda (&rest _)
                          (force-mode-line-update))
                      nil t))
              (buffer-name buf))
          """

        result = subprocess.run(
            [self.emacsclient_path, "--eval", get_buffer_cmd],
            capture_output=True,
            text=True,
            check=True,
        )
        buffer_name = result.stdout.strip().strip('"')

        # Open buffer in Emacs
        cmd = f'(switch-to-buffer "{buffer_name}")'
        subprocess.run(
            [self.emacsclient_path, "-c", "--eval", cmd],
            check=True,
        )

        # Get buffer content after editing
        get_content_cmd = f"""
        (with-current-buffer "{buffer_name}"
            (prog1
                (buffer-string)
                (kill-buffer)))
        """

        result = subprocess.run(
            [self.emacsclient_path, "--eval", get_content_cmd],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip().strip('"')
