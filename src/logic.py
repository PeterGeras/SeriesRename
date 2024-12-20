import os
from pathlib import Path


class UnexpectedFileExtensionError(Exception):
    def __init__(self, filepath, extension, message=None):
        if message is None:
            message = f"Unexpected file extension '{extension}' for file: {filepath}"
        super().__init__(message)
        self.filepath = filepath
        self.extension = extension


def rename_series(series_path: str, series_name: str):
    """
    Generate renaming suggestions for an entire series.
    """
    changes = []

    # Get all season folders
    season_folders = sorted([d for d in os.listdir(series_path) if os.path.isdir(os.path.join(series_path, d))])

    for season_index, season_folder in enumerate(season_folders, start=1):
        season_path = os.path.join(series_path, season_folder)
        new_season_name = f"{series_name}_S{season_index:02d}"
        new_season_path = os.path.join(series_path, new_season_name)

        # First gather changes for files
        changes.extend(rename_episodes_and_subs(season_path, series_name, season_index))
        # Then add the rename for the folder itself
        if season_path != new_season_path:
            changes.append((season_path, new_season_path))

    return changes


def rename_episodes_and_subs(season_path: str, series_name: str, season_index: int):
    """
    Generate renaming suggestions for episodes and subtitles within a season folder.
    """
    changes = []

    season_path = Path(season_path)
    if not season_path.exists():
        season_path = season_path.parent / season_path.name

    episode_files = []
    subtitle_files = []
    allowed_video_extensions = ['.mp4', '.mkv', '.avi']
    allowed_subtitle_extensions = ['.srt', '.sub']

    # Identify episode and subtitle files
    for item in os.listdir(season_path):
        item_path = os.path.join(season_path, item)
        if os.path.isfile(item_path):
            ext = Path(item_path).suffix.lower()
            if ext in allowed_video_extensions:
                episode_files.append(item_path)
            elif ext in allowed_subtitle_extensions:
                subtitle_files.append(item_path)
            else:
                raise UnexpectedFileExtensionError(item_path, ext)

    # Rename episode files and matching subtitles
    for episode_index, episode_path in enumerate(sorted(episode_files), start=1):
        episode_extension = Path(episode_path).suffix
        new_episode_name = f"{series_name}_S{season_index:02d}_E{episode_index:02d}{episode_extension}"
        new_episode_path = os.path.join(season_path, new_episode_name)
        if episode_path != new_episode_path:
            changes.append((episode_path, new_episode_path))

        for subtitle_path in subtitle_files:
            subtitle_extension = Path(subtitle_path).suffix
            new_subtitle_name = f"{series_name}_S{season_index:02d}_E{episode_index:02d}{subtitle_extension}"
            new_subtitle_path = os.path.join(season_path, new_subtitle_name)
            if subtitle_path != new_subtitle_path:
                changes.append((subtitle_path, new_subtitle_path))
            subtitle_files.remove(subtitle_path)
            break

    # Handle subtitles in a "subs" folder (if it exists)
    subs_folder = season_path / "subs"
    if subs_folder.exists() and subs_folder.is_dir():
        subs_files = sorted(subs_folder.iterdir())
        for episode_index, subtitle_path in enumerate(subs_files, start=1):
            subtitle_extension = subtitle_path.suffix
            new_subtitle_name = f"{series_name}_S{season_index:02d}_E{episode_index:02d}{subtitle_extension}"
            new_subtitle_path = subs_folder / new_subtitle_name
            if subtitle_path != new_subtitle_path:
                changes.append((subtitle_path, new_subtitle_path))

    return changes


def execute_changes(changes):
    
    for old_path, new_path in changes:
        if old_path != new_path:
            os.rename(old_path, new_path)
        
