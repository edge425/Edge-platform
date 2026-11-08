exports.handler = async function () {
  const apiKey = process.env.THERUNDOWN_API_KEY;

  if (!apiKey) {
    return {
      statusCode: 500,
      body: JSON.stringify({
        ok: false,
        error: "THERUNDOWN_API_KEY is missing"
      })
    };
  }

  try {
    const response = await fetch(
      "https://therundown.io/api/v2/markets",
      {
        headers: {
          "X-TheRundown-Key": apiKey,
          "Accept": "application/json"
        }
      }
    );

    const body = await response.text();

    return {
      statusCode: response.ok ? 200 : 502,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-store"
      },
      body: JSON.stringify({
        ok: response.ok,
        upstreamStatus: response.status,
        responsePreview: body.slice(0, 1200)
      })
    };
  } catch (error) {
    return {
      statusCode: 502,
      body: JSON.stringify({
        ok: false,
        error: "Unable to contact TheRundown"
      })
    };
  }
};
