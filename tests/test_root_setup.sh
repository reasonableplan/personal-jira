#!/usr/bin/env bash
set -euo pipefail

FAILED=0
PASSED=0

assert_file_exists() {
  if [[ -f "$1" ]]; then
    ((PASSED++))
  else
    echo "FAIL: $1 not found"
    ((FAILED++))
  fi
}

assert_dir_exists() {
  if [[ -d "$1" ]]; then
    ((PASSED++))
  else
    echo "FAIL: directory $1 not found"
    ((FAILED++))
  fi
}

assert_file_contains() {
  if grep -q "$2" "$1" 2>/dev/null; then
    ((PASSED++))
  else
    echo "FAIL: $1 does not contain '$2'"
    ((FAILED++))
  fi
}

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Directory structure
assert_dir_exists "$ROOT/backend"
assert_dir_exists "$ROOT/frontend"
assert_dir_exists "$ROOT/.github"

# Root files
assert_file_exists "$ROOT/.gitignore"
assert_file_exists "$ROOT/README.md"
assert_file_exists "$ROOT/.editorconfig"
assert_file_exists "$ROOT/.env.example"

# .gitignore coverage
assert_file_contains "$ROOT/.gitignore" "__pycache__"
assert_file_contains "$ROOT/.gitignore" ".venv"
assert_file_contains "$ROOT/.gitignore" "node_modules"
assert_file_contains "$ROOT/.gitignore" ".DS_Store"
assert_file_contains "$ROOT/.gitignore" "docker-compose.override.yml"
assert_file_contains "$ROOT/.gitignore" ".env"

# .env.example keys
assert_file_contains "$ROOT/.env.example" "POSTGRES_USER"
assert_file_contains "$ROOT/.env.example" "POSTGRES_PASSWORD"
assert_file_contains "$ROOT/.env.example" "POSTGRES_DB"
assert_file_contains "$ROOT/.env.example" "POSTGRES_PORT=5434"

# .editorconfig
assert_file_contains "$ROOT/.editorconfig" "indent_style"
assert_file_contains "$ROOT/.editorconfig" "charset"
assert_file_contains "$ROOT/.editorconfig" "root = true"

# README.md sections
assert_file_contains "$ROOT/README.md" "기술 스택"
assert_file_contains "$ROOT/README.md" "로컬 실행"
assert_file_contains "$ROOT/README.md" "디렉토리 구조"

echo "\nResults: $PASSED passed, $FAILED failed"
[[ $FAILED -eq 0 ]] && exit 0 || exit 1
