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

function addAPFlagWhenPickupModel(code, model, flag) {
  code.push(["GETLOCAL", 1]);
  code.push(["PUSHINT", model]);

  // If picked-up model does not match, skip this flag block.
  code.push(["JMPNE", 5]);

  code.push(["GETGLOBAL", "fn29"]);
  code.push(["PUSHINT", flag]);
  code.push(["PUSHINT", 1]);
  code.push(["CALL", 0, 0]);

  code.push("REJOIN");
}

function addAnthonyGenericPickupAPFlags(iso) {
  const code = [];

  // Anthony - Weak Alignment Codex
  // Chattur'gha route weak codex = Xel'lotath Codex model 255
  // Ulyaoth route weak codex = Chattur'gha Codex model 245
  // Xel'lotath route weak codex = Ulyaoth Codex model 254
  addAPFlagWhenPickupModel(code, 255, 1148);
  addAPFlagWhenPickupModel(code, 245, 1148);
  addAPFlagWhenPickupModel(code, 254, 1148);

  // Anthony - Antorbok Codex
  addAPFlagWhenPickupModel(code, 242, 1149);

  // Anthony - Magormor Codex
  addAPFlagWhenPickupModel(code, 246, 1150);

  // Anthony - Enchant Item Scroll
  addAPFlagWhenPickupModel(code, 0x20, 1151);

  // Patch the same generic magic pickup handlers edrandomizer patches.
  modifyScript(iso, 1985, s => {
    s.addJmpPatch(6, 9, code);
  });

  modifyScript(iso, 2022, s => {
    s.addJmpPatch(6, 10, code);
  });

  modifyScript(iso, 402, s => {
    s.addJmpPatch(6, 10, code);
  });

  modifyScript(iso, 451, s => {
    s.addJmpPatch(6, 10, code);
  });
}

function applyAnthonyAPPreAlphaPatch(iso) {
  console.log("Applying Eternal Darkness Anthony AP Pre-Alpha patch...");
  
  addAPFlagToEnd(iso, 1360, 1145); // Weak Alignment Rune variant
  addAPFlagToEnd(iso, 1361, 1145); // Weak Alignment Rune variant
  addAPFlagToEnd(iso, 1362, 1145); // Weak Alignment Rune variant
  addAPFlagToEnd(iso, 1368, 1146); // Antorbok Rune
  addAPFlagToEnd(iso, 1369, 1147); // Magormor Rune

  addAnthonyGenericPickupAPFlags(iso); // Codices + Enchant Item Scroll pickup checks

  console.log("Anthony AP Pre-Alpha patch complete.");
}
