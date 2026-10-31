import os
import shutil
import tempfile
import unittest
from gravedigger.models import Tombstone
from gravedigger.ast_scanner import ASTGraveyardScanner
from gravedigger.git_archeologist import GitArcheologist
from gravedigger.necromancer_engine import NecromancerEngine

class TestGraveDigger(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="gravedigger_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_ast_scanner_detects_zombies(self):
        # Create a Python file with one active function and one zombie uncalled function
        py_file = os.path.join(self.test_dir, "sample_module.py")
        with open(py_file, "w") as f:
            f.write(
                "def active_function():\n"
                "    return 42\n\n"
                "def zombie_forgotten_function():\n"
                "    '''This function is unreferenced and dead.'''\n"
                "    return 'brains'\n\n"
                "print(active_function())\n"
            )

        scanner = ASTGraveyardScanner(self.test_dir)
        zombies = scanner.scan_for_zombie_symbols()
        
        # Verify zombie function was identified
        zombie_names = [z.name for z in zombies]
        self.assertIn("zombie_forgotten_function", zombie_names)
        self.assertNotIn("active_function", zombie_names)

    def test_git_archeologist_fallback(self):
        archeologist = GitArcheologist(self.test_dir)
        tombstones = archeologist.excavate_deleted_files()
        self.assertGreater(len(tombstones), 0)
        self.assertTrue(tombstones[0].resurrectable)

    def test_necromancer_resurrection(self):
        engine = NecromancerEngine(self.test_dir)
        report = engine.run_excavation()
        self.assertGreater(report.total_tombstones, 0)

        # Resurrect the first tombstone
        target_id = report.tombstones[0].id
        result = engine.resurrect_tombstone(target_id)
        
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(result.resurrected_path))
        self.assertTrue(os.path.exists(result.patch_path))

        # Check patch content
        with open(result.patch_path, "r") as pf:
            patch_data = pf.read()
            self.assertIn("--- /dev/null", patch_data)
            self.assertIn("+++ b/", patch_data)

if __name__ == "__main__":
    unittest.main()
