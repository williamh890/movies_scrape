import pathlib as pl
import json
import contextlib

from PIL import Image
import numpy as np

IMAGE_DIR_PATH = pl.Path(__file__).parent / '../movie-posters/w500'
IMG_WIDTH, IMG_HEIGHT = 25, 9


def main():
    images = []
    image_paths = list(
        filter(lambda p: not p.is_dir(), IMAGE_DIR_PATH.iterdir())
    )

    for i, img_path in enumerate(image_paths):
        if i % IMG_WIDTH == 0:
            row = []
            images.append(row)

        with open_img(img_path) as img:
            row.append(np.array(img))

    print(len(images))
    rows = [np.concatenate(row, axis=1) for row in images]
    total = np.concatenate(rows, axis=0)

    print(total.shape)

    total_img = Image.fromarray(total)
    total_img.save('mosaic.png')


def misses():
    with open('../movies.csv', 'r') as f:
        movies = set(f.read().strip().split('\n'))

    movie_posters = set(i.stem for i in IMAGE_DIR_PATH.iterdir())
    print(json.dumps(list(movies - movie_posters), indent=2))


def size_check():
    sizes = {}
    for img in IMAGE_DIR_PATH.iterdir():
        with open_img(str(img)) as im:
            if not str(im.size) in sizes:
                sizes[str(im.size)] = [str(img)]
            else:
                sizes[str(im.size)].append(str(img))

    print(json.dumps(sizes, indent=2))


@contextlib.contextmanager
def open_img(path):
    try:
        im = Image.open(path)
        yield im
    except Exception as e:
        raise e
    finally:
        im.close()


if __name__ == "__main__":
    main()
