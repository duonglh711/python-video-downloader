from file_downloader import file_downloader


def find_prefix_path(m3u8_path):
    sub_path = m3u8_path.split("/")
    sub_path.remove(sub_path[-1])
    return "/".join(sub_path)


def parse_m3u8_file(m3u8_path, prefix=True):
    m3u8_file = file_downloader(m3u8_path)
    if "#EXTM3U" not in m3u8_file:
        raise BaseException("It is not a standard m3u8 file.")
    if prefix:
        prefix_path = find_prefix_path(m3u8_path)
    else:
        prefix_path = None
    video_list = []
    lines = m3u8_file.split()
    for line in lines:
        if line.endswith("m3u8"):
            _, sub_list = parse_m3u8_file("/".join([prefix_path, line]), False)
            for path in sub_list:
                video_list.append(path)
        elif line.endswith("ts"):
            video_list.append(line)
    return prefix_path, video_list
