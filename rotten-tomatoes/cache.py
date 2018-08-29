import pathlib as pl
import json


def cache_json(fn):
    def wrapper(*args, **kwargs):
        cache = pl.Path(__file__).parent / 'cache' / fn.__name__ / f'{args[0]}.json'
        cache.parent.mkdir(exist_ok=True, parents=True)

        if cache.exists():
            with cache.open('r') as f:
                return json.load(f)
        else:
            try:
                result = fn(*args, **kwargs)
            except Exception as e:
                raise e
            else:
                with cache.open('w') as f:
                    json.dump(result, f)

                return result

    return wrapper
