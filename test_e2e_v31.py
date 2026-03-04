# -*- coding: utf-8 -*-
"""
OpenClaw SYNC Spectrum Profiler v3.1 — End-to-End Test
Covers: Mock scenarios, OpenClaw standard JSON, Directory structure
"""
import json, os, sys, tempfile, shutil, traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from profiler import run_profile, load_from_bundle, load_from_dir
from data_parser import DataParser, SessionParser
from mock_scenarios import get_all_scenarios

_PASS = 0
_FAIL = 0
_ERRORS = []

def _ok(name, msg=""):
    global _PASS; _PASS += 1
    print(f"  OK  {name}" + (f" -- {msg}" if msg else ""))

def _fail(name, msg=""):
    global _FAIL; _FAIL += 1
    _ERRORS.append(f"{name}: {msg}")
    print(f"  FAIL {name}" + (f" -- {msg}" if msg else ""))

def _check(cond, name, msg=""):
    (_ok if cond else _fail)(name, msg)

def _validate_result(result, label):
    for key in ("bond", "echo", "sync"):
        _check(key in result, f"{label}: has '{key}'")
    bond = result.get("bond", {})
    _check("type_code" in bond or "code" in bond, f"{label}: bond has type code", f"keys={list(bond.keys())[:6]}")
    echo = result.get("echo", {})
    _check("type_code" in echo or "code" in echo, f"{label}: echo has type code", f"keys={list(echo.keys())[:6]}")
    sync = result.get("sync", {})
    _check("primary_type" in sync or "primary" in sync or "type" in sync, f"{label}: sync has primary type", f"keys={list(sync.keys())[:6]}")
    bond_code = bond.get("type_code", bond.get("code", ""))
    if bond_code:
        _check(len(bond_code) == 4 and bond_code.isalpha(), f"{label}: bond code format", f"'{bond_code}'")
    echo_code = echo.get("type_code", echo.get("code", ""))
    if echo_code:
        _check(len(echo_code) == 4 and echo_code.isalpha(), f"{label}: echo code format", f"'{echo_code}'")

# ===== TEST 1: Mock Scenarios =====
def test_mock():
    print("\n" + "="*70)
    print("TEST 1: Mock Scenarios")
    print("="*70)
    all_scenarios = get_all_scenarios()
    scenario_names = list(all_scenarios.keys())
    _check(len(scenario_names) >= 3, "get_all_scenarios >= 3", f"found {len(scenario_names)}: {scenario_names}")
    for name, builder in all_scenarios.items():
        print(f"\n  --- mock: {name} ---")
        try:
            data = builder()
            _check(data is not None, f"scenario_{name}() returns data")
            result = run_profile(data)
            _check(result is not None, f"run_profile('{name}')")
            if result:
                _validate_result(result, f"mock/{name}")
        except Exception as e:
            _fail(f"mock/{name}", f"{type(e).__name__}: {e}")
            traceback.print_exc()
# ===== TEST 2: OpenClaw JSON Formats =====
OC_SESSION = {
    "session_id": "test_001",
    "messages": [
        {"role": "user", "content": "你好，我想了解一下你的功能"},
        {"role": "assistant", "content": "你好！我可以帮你完成代码编写、问题分析等任务。"},
        {"role": "user", "content": "帮我写一个排序函数"},
        {"role": "assistant", "content": "好的，这是快速排序实现。"},
        {"role": "user", "content": "能解释时间复杂度吗？"},
        {"role": "assistant", "content": "快排平均 O(n log n)，最坏 O(n^2)。"},
        {"role": "user", "content": "如何保证 O(n log n)？"},
        {"role": "assistant", "content": "建议用归并排序，所有情况都是 O(n log n)。"},
    ],
    "tool_calls": [{"name": "Write", "arguments": {"path": "sort.py"}}]
}

OC_BUNDLE = {
    "soul": "你是专业编程助手，擅长 Python 和算法。风格简洁专业。",
    "identity": "# Agent Identity\nName: CodeHelper\nRole: Programming Assistant",
    "user": "# User\n资深开发者，关注代码质量。",
    "sessions": [
        {"session_id": "s1", "messages": [
            {"role": "user", "content": "帮我写二叉搜索树"},
            {"role": "assistant", "content": "好的，以下是 BST 实现。"},
            {"role": "user", "content": "加上插入和查找"},
            {"role": "assistant", "content": "已添加 insert 和 search，O(log n)。"},
        ]},
        {"session_id": "s2", "messages": [
            {"role": "user", "content": "上次的 BST 有问题"},
            {"role": "assistant", "content": "什么错误？"},
            {"role": "user", "content": "重复值没处理"},
            {"role": "assistant", "content": "已修复：重复值默认跳过。"},
            {"role": "user", "content": "好的谢谢"},
            {"role": "assistant", "content": "不客气！有问题随时找我。"},
        ]}
    ]
}

SIMPLE_BUNDLE = {
    "user_messages": ["你好", "帮我查天气", "北京明天下雨吗", "谢谢"],
    "agent_messages": ["你好！", "帮你查询天气。", "明天多云，降雨概率20%。", "不客气！"]
}

V3_RECORDS = {
    "soul_text": "你是友善的通用助手。",
    "sessions": [[
        {"type": "message", "role": "user", "content": "你好"},
        {"type": "message", "role": "assistant", "content": "你好！"},
        {"type": "message", "role": "user", "content": "写首诗"},
        {"type": "message", "role": "assistant", "content": "春风拂面花自开。"},
    ]]
}

def test_json_formats():
    print("\n" + "="*70)
    print("TEST 2: OpenClaw JSON Formats")
    print("="*70)
    cases = [
        ("2a: single session", OC_SESSION),
        ("2b: OpenClaw bundle", OC_BUNDLE),
        ("2c: simple messages", SIMPLE_BUNDLE),
        ("2d: session+tool_calls", OC_SESSION),
        ("2e: v3 records", V3_RECORDS),
    ]
    for label, data in cases:
        print(f"\n  --- {label} ---")
        try:
            result = run_profile(data)
            _check(result is not None, f"{label}: run_profile OK")
            if result:
                _validate_result(result, label)
        except Exception as e:
            _fail(f"{label}", f"{type(e).__name__}: {e}")
            traceback.print_exc()

    # DataParser.parse_bundle direct test
    print(f"\n  --- 2f: DataParser.parse_bundle ---")
    try:
        parsed = DataParser.parse_bundle(OC_BUNDLE)
        _check("sessions" in parsed, "2f: has sessions")
        sessions = parsed.get("sessions", [])
        _check(len(sessions) == 2, "2f: parsed 2 sessions", f"got {len(sessions)}")
        for i, s in enumerate(sessions):
            _check(hasattr(s, 'messages') or hasattr(s, 'get_user_messages'),
                   f"2f: session[{i}] is SessionParser", f"type={type(s).__name__}")
    except Exception as e:
        _fail("2f", f"{type(e).__name__}: {e}")
        traceback.print_exc()

    # SessionParser(dict) test
    print(f"\n  --- 2g: SessionParser(dict) ---")
    try:
        sp = SessionParser(OC_SESSION)
        u = sp.get_user_messages()
        a = sp.get_assistant_messages()
        _check(len(u) == 4, "2g: 4 user msgs", f"got {len(u)}")
        _check(len(a) == 4, "2g: 4 asst msgs", f"got {len(a)}")
        _check(len(sp.tool_calls) >= 1, "2g: tool_calls", f"got {len(sp.tool_calls)}")
    except Exception as e:
        _fail("2g", f"{type(e).__name__}: {e}")
        traceback.print_exc()

    # JSON file bundle test
    print(f"\n  --- 2h: JSON file bundle ---")
    tmpdir = tempfile.mkdtemp(prefix="oc_test_")
    try:
        path = os.path.join(tmpdir, "bundle.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(OC_BUNDLE, f, ensure_ascii=False)
        data = load_from_bundle(path)
        _check(data is not None, "2h: load_from_bundle OK")
        if data:
            result = run_profile(data)
            _check(result is not None, "2h: run_profile from file")
            if result:
                _validate_result(result, "2h")
    except Exception as e:
        _fail("2h", f"{type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# ===== TEST 3: Directory Structure =====
def test_directory():
    print("\n" + "="*70)
    print("TEST 3: Directory Structure")
    print("="*70)
    tmpdir = tempfile.mkdtemp(prefix="oc_dir_")
    try:
        # Standard OpenClaw dir
        print(f"\n  --- 3a: standard dir ---")
        with open(os.path.join(tmpdir, "SOUL.md"), 'w') as f:
            f.write("# Soul\n你是编程导师，擅长教学。")
        with open(os.path.join(tmpdir, "IDENTITY.md"), 'w') as f:
            f.write("# Identity\nName: TutorBot\nRole: 编程导师")
        with open(os.path.join(tmpdir, "USER.md"), 'w') as f:
            f.write("# User\n编程初学者。")

        sess_dir = os.path.join(tmpdir, "sessions")
        os.makedirs(sess_dir, exist_ok=True)

        # JSONL session
        with open(os.path.join(sess_dir, "s1.jsonl"), 'w') as f:
            for rec in [
                {"type": "message", "role": "user", "content": "for 循环怎么用？"},
                {"type": "message", "role": "assistant", "content": "for 循环遍历序列。"},
                {"type": "message", "role": "user", "content": "举个例子"},
                {"type": "message", "role": "assistant", "content": "for i in range(5): print(i)"},
            ]:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')

        # JSON session
        with open(os.path.join(sess_dir, "s2.json"), 'w') as f:
            json.dump({"session_id": "s2", "messages": [
                {"role": "user", "content": "什么是列表推导式？"},
                {"role": "assistant", "content": "[expr for item in iterable if cond]"},
            ]}, f, ensure_ascii=False)

        data = load_from_dir(tmpdir)
        _check(data is not None, "3a: load_from_dir OK")
        if data:
            result = run_profile(data)
            _check(result is not None, "3a: run_profile from dir")
            if result:
                _validate_result(result, "3a")

        # .openclaw/ subdirectory
        print(f"\n  --- 3b: .openclaw/ subdir ---")
        tmpdir2 = tempfile.mkdtemp(prefix="oc_dot_")
        oc = os.path.join(tmpdir2, ".openclaw")
        os.makedirs(oc)
        with open(os.path.join(oc, "SOUL.md"), 'w') as f:
            f.write("# Soul\n创意写作助手。")
        with open(os.path.join(oc, "IDENTITY.md"), 'w') as f:
            f.write("# Identity\nName: WriterBot")
        sd2 = os.path.join(oc, "sessions")
        os.makedirs(sd2)
        with open(os.path.join(sd2, "c1.json"), 'w') as f:
            json.dump({"session_id": "c1", "messages": [
                {"role": "user", "content": "写一首秋天的诗"},
                {"role": "assistant", "content": "秋风起，落叶纷飞如蝴蝶。"},
            ]}, f, ensure_ascii=False)

        data2 = load_from_dir(tmpdir2)
        _check(data2 is not None, "3b: load_from_dir(.openclaw/)")
        if data2:
            result2 = run_profile(data2)
            _check(result2 is not None, "3b: run_profile .openclaw/")
            if result2:
                _validate_result(result2, "3b")
        shutil.rmtree(tmpdir2, ignore_errors=True)

    except Exception as e:
        _fail("Group 3", f"{type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# ===== TEST 4: Edge Cases =====
def test_edge():
    print("\n" + "="*70)
    print("TEST 4: Edge Cases")
    print("="*70)

    print(f"\n  --- 4a: empty sessions ---")
    try:
        result = run_profile({"sessions": []})
        _ok("4a: no crash", f"returned {'None' if result is None else 'result'}")
    except Exception as e:
        _fail("4a: crashed", f"{type(e).__name__}: {e}")

    print(f"\n  --- 4b: soul only ---")
    try:
        result = run_profile({"soul": "测试助手"})
        _ok("4b: no crash", f"returned {'None' if result is None else 'result'}")
    except Exception as e:
        _fail("4b: crashed", f"{type(e).__name__}: {e}")

    print(f"\n  --- 4c: key alias soul_text ---")
    try:
        parsed = DataParser.parse_bundle({"soul_text": "友善助手", "sessions": [
            {"session_id": "a1", "messages": [
                {"role": "user", "content": "测试"}, {"role": "assistant", "content": "收到"}
            ]}
        ]})
        soul = parsed.get("soul_text", parsed.get("soul", ""))
        _check(bool(soul), "4c: soul_text alias", f"soul='{soul[:30]}'")
    except Exception as e:
        _fail("4c", f"{type(e).__name__}: {e}")

# ===== Main =====
def main():
    print("="*70)
    print("OpenClaw SYNC Spectrum Profiler v3.1 -- E2E Test")
    print("="*70)
    test_mock()
    test_json_formats()
    test_directory()
    test_edge()
    print("\n" + "="*70)
    print(f"DONE: {_PASS} passed, {_FAIL} failed")
    if _ERRORS:
        print("\nFailures:")
        for e in _ERRORS:
            print(f"  * {e}")
    print("="*70)
    return 0 if _FAIL == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
