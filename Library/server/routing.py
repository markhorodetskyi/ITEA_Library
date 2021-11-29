import functools

routables = []

def on(action, *, skip_schema_validation=False):
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        inner._on_action = action
        inner._skip_schema_validation = skip_schema_validation
        if func.__name__ not in routables:
            routables.append(func.__name__)
        return inner
    return decorator


def create_route_map(obj):
    routes = {}
    for attr_name in routables:
        try:
            attr = getattr(obj, attr_name)
            action = getattr(attr, '_on_action')

            if action not in routes:
                routes[action] = {}

            routes[action]['_skip_schema_validation'] = \
                getattr(attr, '_skip_schema_validation', False)

            routes[action]['_on_action'] = attr

        except AttributeError:
            continue

    return routes
