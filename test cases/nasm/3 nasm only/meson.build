project('nasm only')

if not add_languages('nasm', required: false)
  error('MESON_SKIP_TEST: nasm not found')
endif

if not ['linux', 'windows'].contains(host_machine.system())
  error('MESON_SKIP_TEST: this test asm is made for Windows and Linux')
endif

if meson.backend().startswith('vs')
  error('MESON_SKIP_TEST: VS backend does not recognise NASM yet')
endif

sources = files('dummy.asm')

dummy = library(
    'dummy',
    sources,
    vs_module_defs: 'dummy.def',
)
