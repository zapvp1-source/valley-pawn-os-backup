import sys
p=sys.argv[1]; blk=open(sys.argv[2]).read()
s=open(p).read()
old_l='''def launch(p, headless=False, args=(), window_size=None, **kw):
    """The scripts' launch. `p` is a started sync_playwright. Raises RuntimeError when the profile is open."""
    if is_running():'''
new_l='''def launch(p, headless=False, args=(), window_size=None, **kw):
    """The scripts' launch. `p` is a started sync_playwright. Raises RuntimeError when the profile is open.
    2026-11-21: with the browser host enabled, attach-listed scripts plug into it; all others run exclusive."""
    cfg = host_config()
    if cfg.get("enabled"):
        if _attach_allowed(cfg, args, kw):
            try:
                return attach(p, window_size, kw.get("viewport"))
            except Exception as e:
                print("vp_browser: attach failed, using own launch:", type(e).__name__, str(e)[:160])
        _make_room_for_exclusive()
    if is_running():'''
old_c='''    try:
        ctx.close()
    except Exception:
        pass
    return wait_closed(timeout=timeout)'''
new_c='''    if getattr(ctx, "shared", False):      # 2026-11-21: attached to the host — disconnect, Chrome stays up
        ctx.close()
        return True
    try:
        ctx.close()
    except Exception:
        pass
    r = wait_closed(timeout=timeout)
    lease_release()                         # hand the profile back to the host (no-op when not ours)
    return r'''
old_k='''# ---------- CLI ----------'''
for o,n in ((old_l,new_l),(old_c,new_c),(old_k,blk+"\n\n"+old_k)):
    assert s.count(o)==1, o[:60]
    s=s.replace(o,n)
open(p,'w').write(s)
print("patched")
