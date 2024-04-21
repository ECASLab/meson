# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Meson development team
from __future__ import annotations
import itertools
import typing as T

from . import ExtensionModule, ModuleReturnValue, ModuleInfo
from .. import build
from .. import mesonlib
from ..interpreter.type_checking import CT_INPUT_KW
from ..interpreterbase.decorators import KwargInfo, typed_kwargs, ContainerTypeInfo
from ..utils import File

if T.TYPE_CHECKING:
    from typing_extensions import TypedDict

    from . import ModuleState
    from ..interpreter import Interpreter
    from ..programs import ExternalProgram

    class BitstreamKwargs(TypedDict):
        bitstream_name: str
        sources: T.List[T.Union[mesonlib.FileOrString, build.CustomTarget, build.CustomTargetIndex, build.GeneratedList]]
        platform: str
        build_target: str

class VitisModule(ExtensionModule):

    INFO = ModuleInfo('FPGA/Xilinx', '1.4.0', unstable=True)

    def __init__(self, interp: Interpreter):
        super().__init__(interp)
        self.tools: T.Dict[str, T.Union[ExternalProgram, build.Executable]] = {}
        self.methods.update({
            'bitstream': self.bitstream,
        })

    def _check_tooling(self, state: ModuleState) -> None:
        self.tools['v++'] = state.find_program('v++')

#todo run this version of meson and check if the kwargs mapped to the name assigned to them
    @typed_kwargs('vitis.bitstream',KwargInfo('bitstream_name', str,required=True),
                    KwargInfo('sources',ContainerTypeInfo(list, (File, str)),listify=True,required=True),
                    KwargInfo('platform',str,required=True),
                    KwargInfo('build_target',str,required=True))
    def bitstream(self, state: ModuleState,
                  args: None,
                  kwargs: BitstreamKwargs) -> ModuleReturnValue:
        if not self.tools:
            self._check_tooling(state)
        bitstream_name, arg_sources = args
        all_sources = self.interpreter.source_strings_to_files(
            list(itertools.chain(arg_sources, kwargs['sources'])))

        xclbin_target = build.CustomTarget(
            F'{bitstream_name}.xclbin',
            state.subdir,
            state.subproject,
            state.environment,
            [self.tools['v++'],
             '--mode hls',
             '-c',
             '--platform '.join(),
             '-t '.join(),
             ],
            all_sources
            )
        return ModuleReturnValue(None, [xclbin_target])


def initialize(interp: Interpreter) -> VitisModule:
    return VitisModule(interp)
