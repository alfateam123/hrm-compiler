# -*- coding: utf-8 -*-
import hrmcompiler.parser as p

class Assembler(object):
    def __init__(self):
        self.code = []
        self.aliases = dict()
        self._gen_label_cnt = 1

    def convert_alias(self, aliasObj):
        self.aliases[aliasObj.symbolic_name] = aliasObj.tile_no

    def convert_assign(self, assignObj):
        if assignObj.src == "emp":
            # copyto
            destination_tile = -1

            if assignObj.dst in self.aliases:
                destination_tile = self.aliases[assignObj.dst]
            else:
                try:
                    destination_tile = int(assignObj.dst)
                except TypeError:
                    raise ValueError("the given tile ({0}) is not an alias nor an int!".format(assignObj.dst))

            self.code.append("copyto {0}".format(destination_tile))

        if assignObj.dst == "emp":
            if assignObj.src == "inbox":
                self.code.append("inbox")
            else:
                # raise NotImplementedError("`copyfrom` is not implemented yet!")
                self._handle_copyfrom(assignObj)

    def _handle_copyfrom(self, assignObj):
        source_tile = -1

        if assignObj.src in self.aliases:
            source_tile = self.aliases[assignObj.src]
        else:
            try:
                source_tile = int(assignObj.src)
            except TypeError:
                    raise ValueError("the given tile ({0}) is not an alias nor an int!".format(assignObj.src))

        self.code.append("copyfrom {0}".format(source_tile))

    def convert_add(self, addObj):
        tile_to_add = -1

        if addObj.addend in self.aliases:
            tile_to_add = self.aliases[addObj.addend]
        else:
            try:
                tile_to_add = int(addObj.addend)
            except TypeError:
                raise ValueError("the given tile is not an alias nor an int!", addObj)

        assert tile_to_add != -1
        self.code.append("add {0}".format(tile_to_add))

    def convert_sub(self, subObj):
        tile_to_sub = -1

        if subObj.subtraend in self.aliases:
            tile_to_sub = self.aliases[subObj.subtraend]
        else:
            try:
                tile_to_sub = int(subObj.subtraend)
            except TypeError:
                raise ValueError("the given tile is not an alias nor an int!", subObj)

        assert tile_to_sub != -1
        self.code.append("sub {0}".format(tile_to_sub))

    def convert_outbox(self, outboxObj):
        self.code.append("outbox")

    def convert_label(self, labelObj):
        self.code.append("{0}:".format(labelObj.label_name))

    def convert_jump(self, jumpObj):
        self.code.append("jmp {0}".format(jumpObj.label_name))

    def convert_condjump(self, condjumpObj):
        self.code.append("{cond} {label}".format(
            cond=condjumpObj.condition,
            label=condjumpObj.label_name))

    def _alias_to_number(self, candidate_alias):
        if candidate_alias in self.aliases:
            return self.aliases[candidate_alias]
        else:
            try:
                return int(candidate_alias)
            except TypeError:
                raise ValueError("the given tile is not an alias nor an int!", candidate_alias)

    def convert_incrop(self, incrObj):
        tile = self._alias_to_number(incrObj.label_name)
        self.code.append("incr {tile}".format(tile=tile))

    def convert_if(self, ifObj):
        def create_adhoc_assembler():
            new_assembler = Assembler()
            new_assembler.aliases = self.aliases
            new_assembler._gen_label_cnt = self._gen_label_cnt
            return new_assembler

        label_cnt = self._gen_label_cnt
        self._gen_label_cnt += 1

        true_branch_assembler = create_adhoc_assembler()
        true_branch_assembler.convert(ifObj.true_branch)
        self._gen_label_cnt = true_branch_assembler._gen_label_cnt

        false_branch_assembler = create_adhoc_assembler()
        false_branch_assembler.convert(ifObj.false_branch)
        self._gen_label_cnt = false_branch_assembler._gen_label_cnt

        self.convert_condjump(p.JumpCondOp("_hrm_"+str(label_cnt), "j"+ifObj.condition))
        for false_branch_codeline in false_branch_assembler.code:
            self.code.append(false_branch_codeline)
        self.convert_jump(p.JumpOp("_hrm_endif_"+str(label_cnt)))
        self.convert_label(p.LabelStmt("_hrm_"+str(label_cnt)))
        for true_branch_codeline in true_branch_assembler.code:
            self.code.append(true_branch_codeline)
        self.convert_label(p.LabelStmt("_hrm_endif_"+str(label_cnt)))

    def convert(self, bytecodeList):
        for bytecode in bytecodeList:
            typeToFunMapping = {
                p.AliasStmt: self.convert_alias,
                p.AssignOp: self.convert_assign,
                p.OutboxOp: self.convert_outbox,
                p.AddOp: self.convert_add,
                p.SubOp: self.convert_sub,
                p.LabelStmt: self.convert_label,
                p.JumpOp: self.convert_jump,
                p.JumpCondOp: self.convert_condjump,
                p.IncrOp: self.convert_incrop,
                p.IfOp: self.convert_if
            }

            try:
                typeToFunMapping[type(bytecode)](bytecode)
            except KeyError:
                print("could not convert `{0}`".format(bytecode))
