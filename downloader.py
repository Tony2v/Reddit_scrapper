import imagehash
import os
import requests
from PIL import Image
from io import BytesIO
from multiprocessing import Pool, cpu_count
from functools import partial
from tqdm import tqdm

def url_save_imag(url: str, dir_path: str):
    '''
    Save image from url with phash value in filename for further filtering. Prior to saving:
    1. convert it to RGB;
    2. resize image up to median values assessed through analytics (chooses the biggest resizing factor calculated from magic numbers median_height, median_width)
    If smth goes wrong with response - silently return None

    :param url: image url
    :param dir_path: dir to save
    :return: url string if everything is ok
    '''
    try:
        response = requests.get(url)
        im = Image.open(BytesIO(response.content)).convert("RGB")
        if im.width > median_width or im.height > median_height:
            width_mult = im.width / median_width
            height_mult = im.height / median_height
            resize_coeff = width_mult if width_mult > height_mult else height_mult
            im = im.resize(size=(int(im.width // resize_coeff), int(im.height // resize_coeff)))

        name = str(imagehash.phash(im))
        im.save(os.path.join(dir_path, name + '.jpg'), 'JPEG', quality=100)
        del im
        return url
    except:
        return None

def download_img_from_urls(dest_path: str):
    '''
    Downloading images from every {subreddit_name}.txt file with urls lying in dest_path dir and put it in diretories with {subreddit_name}s.
    :param dest_path: target directory path with {subreddit_name}.txt files
    :return: None
    '''
    files = os.listdir(dest_path)
    for f_name in files:
        if f_name.startswith('.'):
            continue
        new_dir_path = os.path.join(dest_path, f_name.rstrip('.txt'))
        os.mkdir(new_dir_path)
        with open(os.path.join(dest_path, f_name), 'r') as f:
            urls = list(filter(None, f.read().split('\n')))
            pool = Pool(cpu_count())
            list(tqdm(pool.imap(partial(url_save_imag, dir_path=new_dir_path), urls),
                          total=len(urls), desc=f"{f_name.rstrip('.txt')}:"))
            pool.close()
            pool.join()
    return None

if __name__ == "__main__":
    from argparse import ArgumentParser
    desc_text = "Images loader. If image size will be more than -uh UPPER_HEIGHT or -uw UPPER_WIDTH values: it'll be resized to that values with current aspect ratio"
    parser = ArgumentParser(description=desc_text)
    parser.add_argument("-d", "--dir", type=str, required=True, help="target directory path with {subreddit_name}.txt files")
    parser.add_argument("-uh", "--upper_height", type=float, required=True, help="upper boundary height value")
    parser.add_argument("-uw", "--upper_width", type=float, required=True, help="upper boundary width value")
    args = parser.parse_args()
    median_width = args.upper_width
    median_height = args.upper_height
    download_img_from_urls(args.dir)
    print("Process finished!")