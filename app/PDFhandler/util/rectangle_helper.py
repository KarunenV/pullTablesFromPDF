def do_overlap(rect1, rect2, pixel_diff=5):
    l1x = rect1['x0']
    r1x = rect1['x1']
    l1y = rect1['top']
    r1y = rect1['bottom']

    l2x = rect2['x0']
    r2x = rect2['x1']
    l2y = rect2['top']
    r2y = rect2['bottom']

    # If one rectangle is on left side of other
    if (l1x > r2x or l2x > r1x) and ((abs(l2x - r1x) > pixel_diff) and (abs(l1x - r2x) > pixel_diff)):
        return False

    # If one rectangle is above other
    if (r1y < l2y or r2y < l1y) and ((abs(l2y - r1y) > pixel_diff) and (abs(l1y - r2y) > pixel_diff)):
        return False

    return True


# Return true if the rect space matches any of the rects in the list
def checkIfARectangleMatchesList(rect, rect_list, pixel_diff=5):
    for i, im in enumerate(rect_list):
        overlap = do_overlap(rect, im, pixel_diff)

        if overlap:
            return True

    return False


# Merges a list of dictionary rectangles together, so we have less rectangles to worry about
def merge_rects_dicts(rects, pixel_diff=5):

    previous = len(rects)

    while True:
        clusters = list()
        for rect in rects:
            matched = False
            for cluster in clusters:
                if (do_overlap(rect, cluster, pixel_diff)):
                    matched = True
                    cluster['x0'] = min(cluster['x0'], rect['x0'])
                    cluster['x1'] = max(cluster['x1'], rect['x1'])
                    cluster['top'] = min(cluster['top'], rect['top'])
                    cluster['bottom'] = max(cluster['bottom'], rect['bottom'])

            if (not matched):
                clusters.append(rect)

        

        if (len(clusters) == previous):
            break

        previous = len(clusters)
        rects = clusters     

    
    return clusters

def tupleToRectDict(rect_tuple):
    return {"x0": rect_tuple[0],  "top": rect_tuple[1], "x1": rect_tuple[2], "bottom": rect_tuple[3]}

def RectDictToTuple(rect_dict):
    return [rect_dict["x0"], rect_dict["top"], rect_dict["x1"], rect_dict["bottom"]]

# Merges a list of tuple rectangles together, so we have less rectangles to worry about
def merge_rects_tuples(rects, pixel_diff=5):
    rects = merge_rects_dicts([tupleToRectDict(i) for i in rects], pixel_diff)
    return [RectDictToTuple(i) for i in rects]

