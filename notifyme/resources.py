# -*- coding:utf-8 -*-
# (c) Johannes Fürmann <johannes@weltraumpflege.org>
# http://weltraumpflege.org/~johannes
# This file is part of notifyme.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

def convert_to_path(resource):
    """
    converts `resource` to it's path array, i.e. a list of strings.

    Args:
        resource(str): Resource to convert

    Returns:
        list of strings or empty list if the resource is the root resource.
    """
    path_array = resource.split("/")

    # if the resource had a trainling slash, remove the last empty string.
    if path_array[-1] == '':
        path_array.pop()

    # remove the first empty string
    path_array.pop(0)

    return path_array


def is_valid_resource(resource):
    """
    Determines whether `resource` is a valid resource path.

    Args:
        resource(str): Resource string to check

    Returns:
        `True` if `resource` is a valid resource name
        `False` if `resource is _not_ a valid resource name
    """
    # Resources have to begin with a '/'
    if not resource.startswith("/"):
        return False
    
    # split in resource descriptors
    path = convert_to_path(resource)

    for p in path:
        if not p.isalpha():
            return False

    return True

def is_subresource(child, parent):
    """
    Checks if `child` is a subresource of `parent`.

    Args:
        `child`(str): Potential subresource
        `parent`(str): Potential child

    Returns:
        `True`: if `child` is in fact a child of `parent`
        `False`: if `child` is _not_ a child of `parent`.
    """
    child_path, parent_path = convert_to_path(child), convert_to_path(parent)

    # equal resources are subresources
    if child_path == parent_path:
        return True

    # check if parent is fully represented in child
    for e in zip(child_path, parent_path):
        if e[0] != e[1]:
            return False

    return True
