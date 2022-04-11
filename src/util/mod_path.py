import os

class path:

    def get_parent(loc):                                        # loc should be a path: eg.get_parent(__file__)
        return(os.path.dirname(loc))                            # returns the str of parent path


    def get_root(loc):                                          #loc should be a path: eg.get_root(__file__)
        if "opencv_project" in loc:
            while os.path.split(loc)[1] !=  "opencv_project":   
                loc = os.path.dirname(loc)
            return loc                                          # returns the str of root path
        else:                                                   # prevents looping forever
            raise ValueError("__file__ location not in proper root folder")