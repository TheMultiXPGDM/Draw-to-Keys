import math
from itertools import accumulate
from mathutils import Vector

EPS = 1e-6
AABB_EXPANSION = 0.01

def get_strokes(context):
    """Return all annotation strokes from the current frame."""
    if context.annotation_data is None:
        return []
    strokes = []
    for layer in context.annotation_data.layers:
        frame = layer.active_frame
        if frame and frame.strokes:
            strokes.extend(frame.strokes)
    return strokes

def get_stroke_aabb(stroke, expand=0.0):
    """AABB of a whole stroke."""
    coords = [p.co for p in stroke.points]
    x_co = [c[0] for c in coords]
    y_co = [c[1] for c in coords]
    z_co = [c[2] for c in coords]
    return {
        "x0": min(x_co) - expand,
        "x1": max(x_co) + expand,
        "y0": min(y_co) - expand,
        "y1": max(y_co) + expand,
        "z0": min(z_co) - expand,
        "z1": max(z_co) + expand,
    }

def get_segment_aabb(A, B, expand=0.0):
    """AABB of a segment between two points."""
    return {
        "x0": min(A.co[0], B.co[0]) - expand,
        "x1": max(A.co[0], B.co[0]) + expand,
        "y0": min(A.co[1], B.co[1]) - expand,
        "y1": max(A.co[1], B.co[1]) + expand,
        "z0": min(A.co[2], B.co[2]) - expand,
        "z1": max(A.co[2], B.co[2]) + expand,
    }

def test_aabb(A, B):
    """Check if two AABB boxes intersect."""
    if not (B["x0"] <= A["x1"] and A["x0"] <= B["x1"]):
        return False
    if not (B["y0"] <= A["y1"] and A["y0"] <= B["y1"]):
        return False
    return (B["z0"] <= A["z1"] and A["z0"] <= B["z1"])

def get_main_path(strokes):
    """Select the stroke that is longest and most 'wiggly' as the main path."""
    bestidx = -1
    bestscore = 0.0
    bestlengths = None

    for i, stroke in enumerate(strokes):
        points = stroke.points
        lengths = [math.dist(points[i].co, points[i + 1].co) for i in range(len(points) - 1)]
        arclen = sum(lengths)
        arccrd = math.dist(points[0].co, points[-1].co)
        arcwig = 0.0 if arccrd < EPS else arclen / arccrd
        score = 0.7 * arclen + 0.3 * arcwig
        if score > bestscore:
            bestscore = score
            bestidx = i
            bestlengths = lengths

    cumul = [0] + list(accumulate(bestlengths))
    return {
        "idx": bestidx,
        "stroke": strokes[bestidx],
        "count": len(strokes[bestidx].points),
        "lengths": bestlengths,
        "cumulative": cumul,
        "length": cumul[-1],
    }

def get_candidates(strokes, mainstroke):
    """Return list of candidate intersections (stroke index, main segment, stroke segment)."""
    main_aabb = get_stroke_aabb(mainstroke["stroke"], AABB_EXPANSION)
    main_segments_aabb = [
        get_segment_aabb(mainstroke["stroke"].points[i], mainstroke["stroke"].points[i + 1], AABB_EXPANSION)
        for i in range(mainstroke["count"] - 1)
    ]
    strokes_aabb = [get_stroke_aabb(stroke, AABB_EXPANSION) for stroke in strokes]

    broad_cads = []
    for i, stroke in enumerate(strokes):
        if i == mainstroke["idx"]:
            continue
        if test_aabb(strokes_aabb[i], main_aabb):
            broad_cads.append(i)

    semi_narrow = []
    for idx in broad_cads:
        for i in range(mainstroke["count"] - 1):
            if test_aabb(strokes_aabb[idx], main_segments_aabb[i]):
                semi_narrow.append({"stroke": idx, "segment": i})

    narrow = []
    for semi in semi_narrow:
        stroke = strokes[semi["stroke"]]
        points = stroke.points
        for i in range(len(points) - 1):
            s_aabb = get_segment_aabb(points[i], points[i + 1], AABB_EXPANSION)
            if test_aabb(main_segments_aabb[semi["segment"]], s_aabb):
                narrow.append({"stroke": semi["stroke"], "stroke_seg": i, "main_seg": semi["segment"]})
    return narrow

def intersect_segments(a0, a1, b0, b1):
    """
    Compute closest point on two segments.
    Returns a dict with 'parallel' bool, 's', 't' (parametric values) and
    direction vectors if not parallel.
    """
    da = (a1[0] - a0[0], a1[1] - a0[1], a1[2] - a0[2])
    db = (b1[0] - b0[0], b1[1] - b0[1], b1[2] - b0[2])
    r = (b0[0] - a0[0], b0[1] - a0[1], b0[2] - a0[2])

    lenA_sq = da[0] ** 2 + da[1] ** 2 + da[2] ** 2
    lenB_sq = db[0] ** 2 + db[1] ** 2 + db[2] ** 2
    dot_dir = da[0] * db[0] + da[1] * db[1] + da[2] * db[2]
    proj_A = r[0] * da[0] + r[1] * da[1] + r[2] * da[2]
    proj_B = r[0] * db[0] + r[1] * db[1] + r[2] * db[2]

    det = lenA_sq * lenB_sq - dot_dir * dot_dir
    relative_eps = 1e-12 * max(lenA_sq, lenB_sq, 1.0)

    if det < relative_eps:
        return {"parallel": True, "s": 0, "t": 0, "sq_dist": 0}

    s = (lenB_sq * proj_A - dot_dir * proj_B) / det
    t = (dot_dir * proj_A - lenA_sq * proj_B) / det
    s = max(min(s, 1), 0)
    t = max(min(t, 1), 0)

    return {"parallel": False, "s": s, "t": t, "da": da, "db": db}

def auto_calc_threshold(context):
    """Calculate threshold based on view distance."""
    if context.space_data and context.space_data.region_3d:
        view_dist = context.space_data.region_3d.view_distance
        return max(0.0001, min(1.0, view_dist * 0.001))
    return 0.001

def get_intersections(context, candidates, strokes, mainstroke):
    """Compute actual 3D intersection points with deduplication."""
    props = context.scene.draw2keys_props
    threshold = auto_calc_threshold(context) if props.auto_threshold else props.intersect_threshold

    raw = []
    for cad in candidates:
        stroke = strokes[cad["stroke"]]
        seg_idx = cad["stroke_seg"]
        s_a0 = stroke.points[seg_idx].co
        s_a1 = stroke.points[seg_idx + 1].co

        m_seg = cad["main_seg"]
        s_b0 = mainstroke["stroke"].points[m_seg].co
        s_b1 = mainstroke["stroke"].points[m_seg + 1].co

        res = intersect_segments(s_a0, s_a1, s_b0, s_b1)
        if res["parallel"]:
            if props.debug:
                print(f"Parallel: stroke {cad['stroke']}, main {cad['main_seg']}")
            continue

        da, db = res["da"], res["db"]
        s, t = res["s"], res["t"]
        pa = (s_a0[0] + da[0] * s, s_a0[1] + da[1] * s, s_a0[2] + da[2] * s)
        pb = (s_b0[0] + db[0] * t, s_b0[1] + db[1] * t, s_b0[2] + db[2] * t)
        dist = math.dist(pa, pb)
        if dist > threshold:
            if props.debug:
                print(f"Too far: {dist:.6e} > {threshold:.6e}")
            continue

        val = mainstroke["cumulative"][m_seg] + mainstroke["lengths"][m_seg] * t
        raw.append({
            "point": pb,
            "value": val,
            "stroke": cad["stroke"],
            "dist": dist,
            "main_seg": m_seg,
        })

    if not raw:
        return []

    # spatial deduplication
    unique = []
    for inter in raw:
        if not any(math.dist(existing["point"], inter["point"]) < threshold for existing in unique):
            unique.append(inter)
    return unique

def get_action_fcurves(action):
    """Extract fcurves from an Action (works with legacy and new NLA structures)."""
    if hasattr(action, "fcurves"):
        return action.fcurves
    if hasattr(action, "layers") and action.layers:
        layer = action.layers[0]
        if hasattr(layer, "strips") and layer.strips:
            strip = layer.strips[0]
            if hasattr(strip, "channelbags") and strip.channelbags:
                bag = strip.channelbags[0]
                if hasattr(bag, "fcurves") and bag.fcurves:
                    return bag.fcurves
        if hasattr(layer, "fcurves"):
            return layer.fcurves
    return None