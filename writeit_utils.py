"""A utility function for escaping all the values in a dictionary.

We should find a much better place to put this.
"""

from django.utils.html import escape


def escape_dictionary_values(d):
    """Make a new dictionary with same keys but values HTML escaped.

    Since we're potentially making HTML based on user generated input
    and not using the django templating system, we need to make sure
    everything is escaped.
    """
    return dict(
        [(key, escape(value)) for (key, value) in d.items()]
        )
