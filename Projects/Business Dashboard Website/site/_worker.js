// Edge password gate for the Valley Pawn dashboard (HTTP Basic Auth).
// Runs on every request before any asset is served.
export default {
  async fetch(request, env) {
    const expected = "Basic " + btoa("valleypawn:XUmuLL0txKIfcOIHkMSo");
    const auth = request.headers.get("Authorization");
    if (auth !== expected) {
      return new Response("Valley Pawn Dashboard — authentication required.", {
        status: 401,
        headers: { "WWW-Authenticate": 'Basic realm="Valley Pawn Dashboard", charset="UTF-8"' },
      });
    }
    return env.ASSETS.fetch(request);
  },
};
