# SPDX-License-Identifier: Apache-2.0
# Copyright 2024 The Meson development team
from __future__ import annotations
import itertools
import typing as T
import os

from . import ExtensionModule, ModuleReturnValue, ModuleInfo
from .. import build
from .. import mesonlib
from ..interpreter.type_checking import CT_INPUT_KW
from ..interpreterbase.decorators import KwargInfo, typed_kwargs, ContainerTypeInfo


if T.TYPE_CHECKING:
    from typing_extensions import TypedDict

    from . import ModuleState
    from ..interpreter import Interpreter
    from ..programs import ExternalProgram

    class XOKwargs(TypedDict):
        bitstream_name: str
        sources: T.List[T.Union[mesonlib.FileOrString, build.CustomTarget, build.CustomTargetIndex, build.GeneratedList]]
        platform: str
        build_target: str
        executable: build.Executable
        kernel: str
        kernel_frequency: str
        kernel_src_dir: str

class VitisModule(ExtensionModule):

    INFO = ModuleInfo('vitis', '1.4', unstable=True)

    def __init__(self, interp: Interpreter) -> None:
        super().__init__(interp)
        self.tools: T.Dict[str, T.Union[ExternalProgram, build.Executable]] = {}
        self.methods.update({
            'generate_xo': self.generate_xo,
        })

    def _check_tooling(self, state: ModuleState) -> None:
        self.tools['v++'] = state.find_program('v++')


    @typed_kwargs('vitis.generate_xo',
                  KwargInfo('sources',ContainerTypeInfo(list, mesonlib.File),listify=True,required=True),
                  KwargInfo('platform',str,required=True),
                  KwargInfo('build_target',str, required=True),
                  KwargInfo('kernel',str,required=True),
                  KwargInfo('kernel_src_dir',str,default=''))
    def generate_xo(self, state: ModuleState,
                    args: None,
                    kwargs: XOKwargs) -> ModuleReturnValue:
        if not self.tools:
            self._check_tooling(state)
        platform = kwargs['platform']
        kernel = kwargs['kernel']
        xo_sources = kwargs['sources']
        build_target = kwargs['build_target']
        kernel_src_dir = kwargs['kernel_src_dir']
        state.environment.private_dir = f'{state.environment.build_dir}/_x.{build_target}.{platform}'
        xo_target = build.CustomTarget(
        '{}'.format(kernel,'.xo'),
        environment =state.environment,
        outputs= [f'{kernel}.xo'],
        subdir=state.subdir,
        sources=xo_sources,
        subproject= state.subproject,
        command=[
            self.tools['v++'],
            '-c',
            '-g',
            '-t',
            build_target,
            '--platform',
            platform,
            '-k',
            kernel,
            '-I',
            f'{state.environment.build_dir}/{kernel_src_dir}',
            '--temp_dir',
            '@PRIVATE_DIR@',
            '-o',
            f'{state.environment.scratch_dir}/{kernel}.xo',
            xo_sources
            ],
            console=True,
            build_by_default=True,
            build_always_stale=True,
            backend=state.backend
            )
        return ModuleReturnValue(None,[xo_target])


#    @typed_kwargs('vitis.generate_xclbin',
#                    KwargInfo('bitstream_name', str,required=True),
#                    KwargInfo('sources',ContainerTypeInfo(list, mesonlib.File),listify=True,required=True),
#                    KwargInfo('platform',str,required=True),
#                    KwargInfo('build_target',str,required=True),
#                    KwargInfo('kernel', str, default=''),
#                    KwargInfo('kernel_frequency',str,default=''),
#                    KwargInfo('kernel_src_dir',str,required=True))
#    def generate_xclbin(self, state: ModuleState,
#                    args: None,
#                    kwargs: BitstreamKwargs) -> ModuleReturnValue:
#        xclbin_target = build.CustomTarget(
#            '{}'.format(bitstream_name,'.link.xclbin'),
#            environment =state.environment,
#            outputs= [f'{kernel}.link.xclbin'],
#            subdir=state.subdir,
#            sources=[xo_target],
#            subproject= state.subproject,
#            command=[
#                self.tools['v++'],
#                '-l',
#                '-g',
#                '--save-temps',
#                '-t',
#                build_target,
#                '--platform',
#                platform,
#                '--temp_dir',
#                f'./_x.{build_target}.{platform}',
#                '-o',
#                f'./_x.{build_target}.{platform}/{kernel}.link.xclbin',
#                f'./_x.{build_target}.{platform}/{kernel}.xo'
#                ],
#                console=True,
#                build_by_default=True,
#                build_always_stale=True,
#                backend=state.backend.generate_regen_info
#                )


def initialize(interp: Interpreter) -> VitisModule:
    return VitisModule(interp)
