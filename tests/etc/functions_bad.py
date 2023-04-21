# -*- coding: utf-8 -*-
# (c) 2020 The mqttwarn developers

def foobar():
    """
    This function has an intentional indentation error, for
    validating mqttwarn runtime behavior with bogus Python code.
    """
     foo
    return True
