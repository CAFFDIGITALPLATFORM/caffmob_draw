#!/usr/bin/env bash
# (063 RF-02; D-02) Portão local, sempre com recursos de usuário isolados.
set -u
set -o pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
entrega=$(dirname -- "$root")
default_blender=/tmp/claude-0/-home-dev-workspace-caff-systems/8948a4a0-7836-421c-97ad-7fab9159df01/scratchpad/blender/blender-5.2.2-linux-x64/blender
if [[ ! -x "$default_blender" ]] && command -v blender >/dev/null 2>&1; then
    default_blender=$(command -v blender)
fi
blender=${BLENDER_BIN:-$default_blender}
export BLENDER_USER_RESOURCES=${BLENDER_USER_RESOURCES:-$entrega/blender-usuario}
# Nenhum teste deste portão pode usar um MOBI externo.
unset CAFFMOB_ENSAIO_URL
# (067 D-35) O banco do Padrão de Dimensões do portão é descartável: nunca o do titular.
standards_tmp=$(mktemp -d)
trap 'rm -rf -- "$standards_tmp"' EXIT
export CAFFMOB_DRAW_STANDARDS_DB="$standards_tmp/padroes.sqlite3"
mkdir -p "$root/test-results" "$BLENDER_USER_RESOURCES"
log="$root/test-results/portao-$(date -u +%Y%m%dT%H%M%SZ).log"
run_gate() {
    local failed=0 code script
    cd "$root/tests" || return 1
    if [[ -n ${PURE_MODULES:-} ]]; then
        read -r -a modules <<< "$PURE_MODULES"
        python3 -m unittest "${modules[@]}"
    else
        python3 -m unittest discover -p 'test_*.py'
    fi
    code=$?; echo "testes puros: saída $code"; (( code == 0 )) || failed=1
    for module in test_identity test_i18n_coverage; do
        python3 -m unittest "$module"
        code=$?; echo "$module: saída $code"; (( code == 0 )) || failed=1
    done
    cd "$root" || return 1
    for script in ${BLENDER_SCRIPTS:-tests/blender_mobi_operadores.py tests/blender_smoke.py tests/blender_078_openings_and_replace.py tests/blender_080_medidas_reais.py}; do
        "$blender" --background --factory-startup --python-exit-code 1 --python "$script"
        code=$?; echo "$script: saída $code"; (( code == 0 )) || failed=1
    done
    return "$failed"
}
run_gate 2>&1 | tee "$log"
code=${PIPESTATUS[0]}
echo "Portão: saída $code; registro: $log"
exit "$code"
