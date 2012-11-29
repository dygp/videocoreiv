import sys
import idaapi
from idaapi import *

class vciv_processor_t(idaapi.processor_t):
  id = 0x8004
  flag = PR_NO_SEGMOVE | PR_USE32 | PR_CNDINSNS
  plnames = [ 'Broadcom Videocore' ]
  psnames = [ 'vciv' ]
  cnbits = 8
  dnbits = 8
  instruc_start = 0
  segreg_size = 0
  tbyte_size = 0
  assembler = {
    'flag': 0,
    'name': "Custom VCIV assembler",
    'origin': ".origin",
    'end': ".end",
    'cmnt': ";",
    'ascsep': "\"",
    'accsep': "'",
    'esccodes': "\"'",
    'a_ascii': ".ascii",
    'a_byte': ".byte",
    'a_word': ".short",
    'a_dword': ".int",
    'a_qword': ".quad",
    'a_oword': ".dquad",
    'a_float': ".float",
    'a_double': ".double",
    'a_bss': ".bss",
    'a_seg': ".seg",
    'a_curip': "__pc__",
    'a_public': ".public",
    'a_weak': ".weak",
    'a_extrn': ".extrn",
    'a_comdef': ".comdef",
    'a_align': ".align",
    'lbrace': "(",
    'rbrace': ")",
    'a_mod': "%",
    'a_band': "&",
    'a_bor': "|",
    'a_xor': "^",
    'a_bnot': "~",
    'a_shl': "<<",
    'a_shr': ">>",
    'a_sizeof_fmt': "size %s"
  }

  ISA = [
    ["halt", [0x0000], [0xffff], CF_STOP, []],
    ["nop", [0x0001], [0xffff], 0, []],
    ["wait", [0x0002], [0xffff], 0, []],
    ["user", [0x0003], [0xffff], 0, []],
    ["sti", [0x0004], [0xffff], 0, []],
    ["cli", [0x0005], [0xffff], 0, []],
    # ["rts", [0x005a], [0xffff], CF_JUMP | CF_STOP, []],
    ["cpuid", [0x00e0], [0xffe0], CF_CHG1, [[0,5,o_reg]]],
    ["b", [0x0040], [0xffe0], CF_JUMP | CF_USE1 | CF_STOP, [[0,5,o_reg]]],
    ["bl", [0x0060], [0xffe0], CF_CALL | CF_USE1, [[0,5,o_reg]]],
    ["ld", [0x0800], [0xff00], CF_CHG1 | CF_USE2, [[0,4,o_reg],[4,4,o_phrase]]],
    ["st", [0x0900], [0xff00], CF_USE1 | CF_CHG2, [[0,4,o_reg],[4,4,o_phrase]]],
    ["bne", [0x1880], [0xff80], CF_JUMP | CF_USE1, [[0,7,o_near]]],
    ["b", [0x1f00], [0xff80], CF_JUMP | CF_USE1 | CF_STOP, [[0,7,o_near]]],
    ["mov", [0x4000], [0xff00], CF_CHG1 | CF_USE2, [[0,4,o_reg],[4,4,o_reg]]],
    ["add", [0x4200], [0xff00], CF_CHG1 | CF_USE2, [[0,4,o_reg],[4,4,o_reg]]],
    ["sub", [0x4600], [0xff00], CF_CHG1 | CF_USE2, [[0,4,o_reg],[4,4,o_reg]]],
    ["and", [0x4700], [0xff00], CF_CHG1 | CF_USE2, [[0,4,o_reg],[4,4,o_reg]]],
    ["ror", [0x4900], [0xff00], CF_CHG1 | CF_USE2, [[0,4,o_reg],[4,4,o_reg]]],
    ["cmp", [0x4a00], [0xff00], CF_USE1 | CF_USE2, [[0,4,o_reg],[4,4,o_reg]]],
    ["or", [0x4d00], [0xff00], CF_CHG1 | CF_USE2, [[0,4,o_reg],[4,4,o_reg]]],
    ["bl", [0x9080, 0x0000], [0xffff, 0x0000], CF_CALL | CF_USE1, [[16,16,o_near]]],
    ["mov", [0xb000, 0x0000], [0xffe0, 0x0000], CF_CHG1 | CF_USE2, [[0,5,o_reg],[16,16,o_imm]]],
    ["mov", [0xe800, 0x0000, 0x0000], [0xffe0, 0x0000, 0x0000], CF_CHG1 | CF_USE2, [[0,5,o_reg],[16,32,o_imm]]],
    ["add", [0xe840, 0x0000, 0x0000], [0xffe0, 0x0000, 0x0000], CF_CHG1 | CF_USE2, [[0,5,o_reg],[16,32,o_imm]]],
    ["sub", [0xe8c0, 0x0000, 0x0000], [0xffe0, 0x0000, 0x0000], CF_CHG1 | CF_USE2, [[0,5,o_reg],[16,32,o_imm]]],
    ["and", [0xe8e0, 0x0000, 0x0000], [0xffe0, 0x0000, 0x0000], CF_CHG1 | CF_USE2, [[0,5,o_reg],[16,32,o_imm]]],
    ["ror", [0xe920, 0x0000, 0x0000], [0xffe0, 0x0000, 0x0000], CF_CHG1 | CF_USE2, [[0,5,o_reg],[16,32,o_imm]]],
    ["cmp", [0xe940, 0x0000, 0x0000], [0xffe0, 0x0000, 0x0000], CF_USE1 | CF_USE2, [[0,5,o_reg],[16,32,o_imm]]],
    ["or", [0xe9a0, 0x0000, 0x0000], [0xffe0, 0x0000, 0x0000], CF_CHG1 | CF_USE2, [[0,5,o_reg],[16,32,o_imm]]],
  ]

  @staticmethod
  def BITFIELD(word, start, width):
    return (word >> start) & ((1 << width) - 1)
  @staticmethod
  def XBITFIELD(wordarray, start, width):
    v = 0
    while ((start + width - 1)>>4) > (start>>4):
      lastbit = (start + width - 1)
      firstbit = (lastbit & ~0xf)
      lastbithere = (start+width-1) & 0xf
      v |= vciv_processor_t.BITFIELD(wordarray[(start+width-1)>>4], 0, (lastbit+1)&0xf) << (firstbit - start)
      width -= (lastbithere+1)
    v |= vciv_processor_t.BITFIELD(wordarray[start>>4], start & 0x0f, width)
    return v
  @staticmethod
  def SXBITFIELD(wordarray, start, width):
    v = vciv_processor_t.XBITFIELD(wordarray, start, width-1)
    sign = vciv_processor_t.XBITFIELD(wordarray, start+width-1, 1)
    if sign != 0:
      v = -(1 << (width-1)) + v
    return v

  def get_frame_retsize(self, func_ea):
    print "get_frame_retsize"
    return 0

  def notify_get_autocmt(self):
    print "notify_get_autocmt"
    return "No Comment"

  def is_align_insn(self, ea):
    print "is_align_insn"
    return 0

  def notify_newfile(self, filename):
    print "notify_newfile"
    pass

  def notify_oldfile(self, filename):
    print "notify_oldfile"
    pass

  def handle_operand(self, op, isread):
    print "handle_operand"
    if self.cmd.get_canon_feature() & CF_JUMP:
      ua_add_cref(0, op.addr, fl_JN)
    if self.cmd.get_canon_feature() & CF_CALL:
      ua_add_cref(0, op.addr, fl_CN)

    return

  def add_stkvar(self, v, n, flag):
    print "add_stkvar"
    return

  def add_stkpnt(self, phn, v):
    print "add_stkpnt"
    return

  def trace_sp(self):
    print "trace_sp"
    return

  def emu(self):
    # print "emu"
    flags = self.cmd.get_canon_feature()

    if flags & CF_USE1:
      self.handle_operand(self.cmd.Op1, 0)
    if flags & CF_CHG1:
      self.handle_operand(self.cmd.Op1, 1)

    if not (flags & CF_STOP):
      ua_add_cref(0, self.cmd.ea + self.cmd.size, fl_F)

    return 1

  def outop(self, op):
    # print "outop %d" % op.type
    if op.type == o_reg:
      out_register(self.regNames[op.reg])
    elif op.type == o_imm:
      if op.dtyp == dt_word:
        OutValue(op, OOFW_IMM | OOFW_16)
      else:
        OutValue(op, OOFW_IMM | OOFW_32)
    elif op.type == o_near:
      out_name_expr(op, op.addr, BADADDR)
    elif op.type == o_phrase:
      out_symbol('(')
      out_register(self.regNames[op.phrase])
      out_symbol(')')
    else:
      out_symbol('?')
    return True

  def out(self):
    # print "out"
    buf = idaapi.init_output_buffer(128)
    OutMnem()
    if self.cmd.Op1.type != o_void:
      out_one_operand(0)
    if self.cmd.Op2.type != o_void:
      out_symbol(',')
      out_symbol(' ')
      out_one_operand(1)
    if self.cmd.Op3.type != o_void:
      out_symbol(',')
      out_symbol(' ')
      out_one_operand(2)
    if self.cmd.Op4.type != o_void:
      out_symbol(',')
      out_symbol(' ')
      out_one_operand(3)
    term_output_buffer()
    MakeLine(buf)
    return

  def simplify(self):
    # print "simplify"
    return

  def ana(self):
    # print "ana"
    op0 = ua_next_word()
    oplenbits = self.BITFIELD(op0, 8, 8)

    op = [ op0 ]

    if oplenbits < 0x80:
      self.cmd.size = 2
    else:
      op += [ ua_next_word() ]
      if oplenbits < 0xe0:
        self.cmd.size = 4
      else:
        op += [ ua_next_word() ]
        if oplenbits < 0xfa:
          self.cmd.size = 6
        else:
          op += [ ua_next_word() ]
          op += [ ua_next_word() ]
          self.cmd.size = 10

    self.cmd.itype = self.find_insn(op)
    # print "Parsed OP %x (oplenbits %d) to INSN #%d" % ( op0, oplenbits, self.cmd.itype )
    if self.cmd.itype >= self.instruc_end:
      return 0

    args = self.ISA[self.cmd.itype][4]
    if len(args) > 0:
      self.get_arg(op, args[0], self.cmd.Op1)
    if len(args) > 1:
      self.get_arg(op, args[1], self.cmd.Op2)
    if len(args) > 2:
      self.get_arg(op, args[2], self.cmd.Op3)
    if len(args) > 3:
      self.get_arg(op, args[3], self.cmd.Op4)

    return self.cmd.size

  def get_arg(self, op, arg, cmd):
    if len(arg) != 3:
      cmd.type = o_void
    else:
      # print "get_arg %d %d %d => " % (arg[0], arg[1], arg[2])
      boff, bsize, cmd.type = arg
      if cmd.type == o_reg:
        cmd.reg = self.XBITFIELD(op, boff, bsize)
      elif cmd.type == o_imm:
        if bsize <= 16:
          cmd.dtyp = dt_word
        else:
          cmd.dtyp = dt_dword
        cmd.value = self.SXBITFIELD(op, boff, bsize)
      elif cmd.type == o_near:
        cmd.addr = self.cmd.ea + 2 * self.SXBITFIELD(op, boff, bsize)
      elif cmd.type == o_phrase:
        cmd.phrase = self.XBITFIELD(op, boff, bsize)
        cmd.specflags = 0
    # print "get_arg %d (%d %d %d)" % (cmd.type, cmd.reg, cmd.value, cmd.addr)

  def notify_init(self, idp):
    print "notify_init"
    # idaapi.cvar.inf.mf = 1
    return 1

  def find_insn(self, op):
    # print "Searching pattern, OP0 is %d, length %d." % ( op[0], len(op) )
    i = 0
    for insn in self.ISA:
      mnem, patt, mask, fl, args = insn
      if len(mask) == len(op):
        opmasked = [ (op[j] & mask[j]) for j in range(len(op)) ]
        # print (op, mask, opmasked )
        if opmasked == patt:
          # print "Found at %d. (OP/MASK/PATT %d/%d/%d)" % (i, op[0], mask[0], patt[0])
          return i
      i += 1
    return self.instruc_end

  def init_isa(self):
    self.instruc = [ ]
    i = 0
    for insn in self.ISA:
      mnem, patt, mask, fl, args = insn
      self.instruc.append( { 'name': mnem, 'feature': fl } )
      i += 1
    return i

  def __init__(self):
    print "__init__"
    idaapi.processor_t.__init__(self)
    self.regNames = [ "r%d" % d for d in range(0, 31) ]
    for d in range(0, 31):
      setattr(self, 'ireg_%d' % d, d)
    self.regNames += [ "rfoo" ]
    setattr(self, 'ireg_foo', 32)
    self.instruc_end = self.init_isa()
    # setattr(self, 'itype_nop', 0)
    self.comments = { }
    self.regFirstSreg = 32
    self.regLastSreg = 32
    self.regCodeSreg = 32
    self.regDataSreg = 32
    self.PTRSIZE = 4
    self.icode_return = 0

def PROCESSOR_ENTRY():
  # print "Constructing VCIV module"
  return vciv_processor_t()
