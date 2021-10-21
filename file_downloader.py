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
    print("{} is downloading...".format(total_name).center(60, "-"))
    count = 1
    path = save_path + "/" + total_name
    if not os.path.exists(path):
        os.mkdir(path)

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
    print("{} is merging...".format(total_name).center(60, "-"))
    print(len(video_list))
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
