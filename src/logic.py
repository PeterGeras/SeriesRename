import os
from pathlib import Path
from collections import defaultdict


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
    allowed_subtitle_extensions = ['.srt', '.sub', '.idx']

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

    # Group subtitle files by their base name (stem)
    subtitle_groups = group_subtitles_by_stem(subtitle_files)

    # Sort and rename episode files, assigning a subtitle group per episode
    episode_files_sorted = sorted(episode_files)
    subtitle_group_keys = list(subtitle_groups.keys())
    subtitle_group_keys.sort()

    for episode_index, episode_path in enumerate(episode_files_sorted, start=1):
        episode_extension = Path(episode_path).suffix
        new_episode_name = f"{series_name}_S{season_index:02d}_E{episode_index:02d}{episode_extension}"
        new_episode_path = os.path.join(season_path, new_episode_name)
        if episode_path != new_episode_path:
            changes.append((episode_path, new_episode_path))

        # If there's a subtitle group available, rename all files in that group
        if subtitle_group_keys:
            group_key = subtitle_group_keys.pop(0)
            for sub_file_path in subtitle_groups[group_key]:
                subtitle_extension = Path(sub_file_path).suffix
                new_subtitle_name = f"{series_name}_S{season_index:02d}_E{episode_index:02d}{subtitle_extension}"
                new_subtitle_path = os.path.join(season_path, new_subtitle_name)
                if sub_file_path != new_subtitle_path:
                    changes.append((sub_file_path, new_subtitle_path))

    # Handle subtitles in a "subs" folder (if it exists)
    subs_folder = season_path / "subs"
    if subs_folder.exists() and subs_folder.is_dir():
        subs_files = [f for f in subs_folder.iterdir() if f.is_file() and f.suffix.lower() in allowed_subtitle_extensions]
        subs_groups = group_subtitles_by_stem([str(f) for f in subs_files])

        # We assume the subs_folder subtitles are sorted in episode order
        subs_group_keys = list(subs_groups.keys())
        subs_group_keys.sort()
        for episode_index, group_key in enumerate(subs_group_keys, start=1):
            for sub_file_path in subs_groups[group_key]:
                subtitle_extension = Path(sub_file_path).suffix
                new_subtitle_name = f"{series_name}_S{season_index:02d}_E{episode_index:02d}{subtitle_extension}"
                new_subtitle_path = subs_folder / new_subtitle_name
                if str(sub_file_path) != str(new_subtitle_path):
                    changes.append((sub_file_path, str(new_subtitle_path)))

    return changes


def group_subtitles_by_stem(subtitle_files):
    """
    Given a list of subtitle file paths, group them by their stem (filename without extension).
    For example, if we have:
        episode1.sub
        episode1.idx
    They should be grouped together.
    """
    groups = defaultdict(list)
    for f in subtitle_files:
        stem = Path(f).stem
        groups[stem].append(f)
    return groups


def execute_changes(changes):
    for old_path, new_path in changes:
        if old_path != new_path:
            os.rename(old_path, new_path)
