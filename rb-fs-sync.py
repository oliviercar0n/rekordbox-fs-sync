import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
import urllib
import argparse


def read_collection(xml_tree: ET.ElementTree) -> dict:
    collection = {}
    collection_tree = xml_tree.getroot().find("COLLECTION")
    for track in collection_tree:
        location = track.attrib["Location"]
        track_id = track.attrib["TrackID"]
        collection[track_id] = {"location": location}

    return collection


def create_playlist_folder(playlist_node, folder_path, collection):
    playlist_folder_path = folder_path / playlist_node.attrib["Name"]

    if not playlist_folder_path.exists():
        playlist_folder_path.mkdir()

    for track in playlist_node.findall("TRACK"):
        track_location = collection[track.attrib["Key"]]["location"].replace(
            "file://localhost", ""
        )
        unquoted_path = urllib.parse.unquote(track_location)
        source_file_path = Path(unquoted_path)
        shutil.copy(source_file_path, playlist_folder_path)


def process_folder_recursive(node, current_dir, collection):
    folder_name = node.attrib["Name"]
    folder_path = current_dir / folder_name

    if not folder_path.exists():
        folder_path.mkdir()

    for sub_node in node.findall("NODE"):
        if sub_node.attrib["Type"] == "0":
            process_folder_recursive(sub_node, folder_path, collection)
        elif sub_node.attrib["Type"] == "1":
            create_playlist_folder(sub_node, folder_path, collection)


def main():
    parser = argparse.ArgumentParser(
        description="Convert Rekordbox playlists to filesystem folders"
    )
    parser.add_argument("xml_file_path", type=str, help="Path to the XML file.")
    parser.add_argument("music_folder_path", type=str, help="Path to the music folder.")
    args = parser.parse_args()

    tree = ET.parse(args.xml_file_path)
    collection = read_collection(tree)
    playlists_tree = tree.getroot().find("PLAYLISTS")
    process_folder_recursive(
        playlists_tree[0], Path(args.music_folder_path), collection
    )

    print("Sync complete")


if __name__ == "__main__":
    main()
