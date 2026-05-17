function addAPFlagToEnd(iso, scriptId, flag) {
  modifyScript(iso, scriptId, s => {
    const end = s.instructions.length - 1;

    s.instructions.splice(
      end,
      0,
      s.buildInstruction("GETGLOBAL", "fn29"),
      s.buildInstruction("PUSHINT", flag),
      s.buildInstruction("PUSHINT", 1),
      s.buildInstruction("CALL", 0, 0)
    );
  });
}

function insertAPFlag(iso, scriptId, index, flag, callArgs = 0) {
  modifyScript(iso, scriptId, s => {
    s.instructions.splice(
      index,
      0,
      s.buildInstruction("GETGLOBAL", "fn29"),
      s.buildInstruction("PUSHINT", flag),
      s.buildInstruction("PUSHINT", 1),
      s.buildInstruction("CALL", callArgs, 0)
    );
  });
}

function applyAnthonyAPPreAlphaPatch(iso) {
  console.log("Applying Eternal Darkness Anthony AP Pre-Alpha patch...");

  insertAPFlag(iso, 2129, 230, 1144, 0); // 3 Point Circle

  addAPFlagToEnd(iso, 1360, 1145); // Weak Alignment Rune variant
  addAPFlagToEnd(iso, 1361, 1145); // Weak Alignment Rune variant
  addAPFlagToEnd(iso, 1362, 1145); // Weak Alignment Rune variant
  addAPFlagToEnd(iso, 1368, 1146); // Antorbok Rune
  addAPFlagToEnd(iso, 1369, 1147); // Magormor Rune

  addAPFlagToEnd(iso, 1279, 1148); // Weak Alignment Codex
  insertAPFlag(iso, 347, 18, 1149, 1); // Antorbok Codex
  addAPFlagToEnd(iso, 2016, 1150); // Magormor Codex
  addAPFlagToEnd(iso, 2369, 1151); // Enchant Item Scroll

  console.log("Anthony AP Pre-Alpha patch complete.");
}
