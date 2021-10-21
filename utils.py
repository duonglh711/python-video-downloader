import os
import sys
import requests
from multiprocessing import Pool, cpu_count


def view_bar(num, total):
    rate_num = int(num / total * 60)
    r = '\r[%s%s]' % ("#" * rate_num, " " * (60 - rate_num))
    sys.stdout.write(r)
    sys.stdout.write(f' {(rate_num / 3 * 5):.5f}% ')
    sys.stdout.flush()


def file_downloader(url, save_path=None):
    if save_path is not None and os.path.exists(save_path):
        return
    resource = requests.get(url)
    if save_path is not None:
        with open(save_path, mode="wb") as fh:
            fh.write(resource.content)
    else:
        return resource.content.decode(encoding="utf-8", errors="strict")


def download_one_file(prefix_path, file, path, count, len_video):
    file_url = "/".join([prefix_path, file])
    name = path + "/" + file
    file_downloader(file_url, name)
    if count % 30 == 0:
        view_bar(count, len_video)


def ts_download(prefix_path, video_list, total_name, save_path, n_job):
    if total_name is None:
        total_name = "video"

    k = 0
    total_name_temp = total_name
    while os.path.isfile(os.path.join(save_path, total_name + ".mp4")):
        k+=1
        total_name = total_name_temp + str(k)

    print("{}.mp4 is downloading...".format(total_name).center(60, "-"))
    count = 1
    path = os.path.join(save_path, total_name)
    os.makedirs(path, exist_ok = True)

    cpu_number = int(n_job)
    if n_job == -1 or n_job >= cpu_count():
        cpu_number = cpu_count()
    elif n_job < 1:
        cpu_number = int(n_job * cpu_count())
    pool = Pool(cpu_number)
    len_video = len(video_list)
    for file in video_list:
        pool.apply_async(download_one_file, (prefix_path, file, path, count, len_video))
        count += 1

    pool.close()
    pool.join()

    print()
    print("{}.mp4 is merging...".format(total_name).center(60, "-"))
    name = merge(video_list, path)
    os.chdir(path)
    os.system("rename " + name[0] + " " + total_name + ".mp4 ")
    os.system("move " + total_name + ".mp4 ../" + total_name + ".mp4")

    os.chdir(save_path)
    os.system("rd /s /q " + total_name)


def merge(file_list, path):
    if len(file_list) > 2:
        list_a = merge(file_list[0: len(file_list) // 2], path)
        list_b = merge(file_list[len(file_list) // 2:], path)
        return merge(list_a + list_b, path)
    elif len(file_list) == 2:
        os.chdir(path)
        shell_str = "+".join(file_list)
        shell_str = "copy /b " + shell_str + " " + file_list[0] + " > .temp"
        os.system(shell_str)
        for file in file_list:
            if file != file_list[0]:
                os.system("del /Q {}".format(file))
        return [file_list[0]]
    else:
        return file_list


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
