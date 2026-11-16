"""KM LOCAL runtime boot v2 (2026-11-16) for Railway witnessstrictimage.

The repository became private, so the v1 start command (raw.githubusercontent.com
fetch at every start) can no longer boot. The service now builds from this
directory (Railway GitHub integration, pinned commit). Same blobs and SHAs as the
v1 boot: app.py/parameter map/modules from f0d23766, app_v15.py and
source_acquisition.py from b26e49c3; KRS Engine still from KM_ENGINE_GZ_B64_*.
Boot fails closed on any SHA mismatch.
v1.6 (2026-11-16): adds app_v16.py (Rakuten formal SOURCE, Owner instruction) and
rakuten.py (the autopilot's public race-card parser); the pinned v1.5 files are unchanged.
"""
import base64, gzip, hashlib, json, os, pathlib

HERE = pathlib.Path(__file__).resolve().parent / "km"
PIN = {"app.py": "7ca4ea99cf82943ad6255fdc9d7d5d24f1c5f54b5dd9767a22d860dd6f0d2e40", "app_v15.py": "2d4f32ef2ad8d17ac9b0ab8b11581bb5791f96615cc4bb579ae673bc45daa6f1", "app_v16.py": "ebb9c010ba5b690e22e1a1d2f8a03c0c52c13639d07986c00954c53913220d2a", "capital_policy.py": "ce47d40b28f2ebf6716a3e4c796852b5c6c74526b890ede80ef327085d9d1ba6", "jma_weather_evidence.py": "ddf600b9ff25745777865d0eb98c67aefdf4476a64b4b0604b1605e0cef614e1", "krs_prediction_utility.py": "b857634bfea82971c5251524606c7a2af8cfc5004d670fecf6b949213ec76c21", "local_population_ledger.py": "346e3c3289e20aa69fecb587bd9705297ff408becd4390bacee356dff216d850", "minimum_efficient_coverage.py": "2d8ecd9004b57216bd4e516f8f77168962c32abf92a61e0678a38b7c900f7280", "nar_auxiliary_evidence.py": "470e5f1c6a0fcb35363cfe59632b2c00f5d8537d9000e496b399a85c4d61223c", "nar_runner_universe.py": "d2ab387d6ce20bff26b86e3be341fda0777b984a1ff664dc688ee0fde523b7cb", "nar_source_manifest.py": "35cec3b9a7bb313ef1d90a7e7f4f4d1d08ae2f329e05cc563575d82e4c0732cc", "parameter_map_v0.1-provisional.json": "d8c027ee5bcc8fd3d2c248e8059b341776be38910e833d7589f09ab817c161f5", "post_result_learning.py": "b67a70415682db179ac75bfe8ed05b34579b241dbe12bb919550bc554a36d8df", "rakuten.py": "8e17c4f090279141c6317f3e65affcdb0d258a89ac45a23857fde089263cd4a8", "sbo_public_shadow_evidence.py": "998cec5d9b426efaa1a6d8411b2125fd797e39f66ee5bf5dfb46fd8d15148c53", "source_acquisition.py": "ef05cf8bfad137b04b2c21e9dede20b9a5502e60cb9abd2cc13e68c0c33b90a9"}
ENGINE_SHA = "9929df994aa7964173edef9af7e9a705628ce377babf22df3af4e280fc275421"


def main():
    dec = lambda s: gzip.decompress(base64.b64decode(s + "=" * ((-len(s)) % 4)))
    eb = dec("".join(os.environ[f"KM_ENGINE_GZ_B64_{i}"] for i in range(6)))
    esh = hashlib.sha256(eb).hexdigest()
    assert esh == ENGINE_SHA == os.environ["KM_LOCAL_ENGINE_SHA256"], ("ENGINE_SHA_MISMATCH", esh)
    got = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in PIN}
    assert got == PIN, ("KM_LOCAL_CODE_PIN_MISMATCH", got)
    ptr = json.loads((HERE / "current_execution_gateway.json").read_text())
    assert "LOCAL" in ptr["families"]
    o = pathlib.Path("/opt/km")
    o.mkdir(parents=True, exist_ok=True)
    (o / "rev").write_text("b26e49c356749f5ada6d065ab0b615c3675648ab")
    (o / "current_execution_gateway.json").write_text(json.dumps(ptr, sort_keys=True))
    for n in PIN:
        (o / n).write_bytes((HERE / n).read_bytes())
    (o / "KRS-Engine_v1.1.0_PORTABLE.py").write_bytes(eb)
    (o / "param.sha").write_text(PIN["parameter_map_v0.1-provisional.json"])
    print("KM_LOCAL_RUNTIME_BLOBS_REPO_BUILD", esh, json.dumps(PIN, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
