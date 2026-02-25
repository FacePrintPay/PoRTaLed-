#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

# ---------- Colors & echo helpers ----------
BLUE='\033[1;34m'; GREEN='\033[1;32m'; YELLOW='\033[1;33m'; RED='\033[1;31m'; NC='\033[0m'
echo_info()    { echo -e "${BLUE}ℹ️  $1${NC}"; }
echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_warn()    { echo -e "${YELLOW}⚠️  $1${NC}"; }
echo_error()   { echo -e "${RED}❌ $1${NC}"; }

# ---------- Settings ----------
APPS_DIR="${APPS_DIR:-$HOME/aikre8tive/apps}"
REPO_ROOT="${REPO_ROOT:-$HOME/aikre8tive}"
WF_DIR="$REPO_ROOT/.github/workflows"
WF_FILE="$WF_DIR/vercel-matrix.yml"
VERCEL_SCOPE="${VERCEL_SCOPE:-}"        # e.g. your vercel team/org slug
BRANCH_DEFAULT="${BRANCH_DEFAULT:-main}" # or master

mkdir -p "$APPS_DIR" "$WF_DIR"

need() { command -v "$1" >/dev/null 2>&1 || { echo_error "Missing: $1"; exit 1; }; }
need jq
need node
need npm
need vercel
if command -v gh >/dev/null 2>&1; then GH_OK=1; else GH_OK=0; fi

echo_info "Using apps root: $APPS_DIR"

# ---------- Auto-harvest loose HTML into apps if apps/ is empty ----------
if [ -z "$(find "$APPS_DIR" -mindepth 1 -maxdepth 1 -type d)" ]; then
  echo_warn "No app directories found in $APPS_DIR."
  echo_info "Scanning for loose *.html under $REPO_ROOT to auto-create static apps…"
  mapfile -t LOOSE_HTML < <(find "$REPO_ROOT" -maxdepth 2 -type f -name "*.html" ! -path "$APPS_DIR/*" | sort || true)
  if [ ${#LOOSE_HTML[@]} -eq 0 ]; then
    echo_warn "No loose HTML found. Creating demo app 'planetarium'."
    mkdir -p "$APPS_DIR/planetarium/public"
    cat > "$APPS_DIR/planetarium/public/index.html" <<'HTML'
<!doctype html><meta charset="utf-8"><title>Planetarium</title>
<h1 style="font-family:system-ui;margin:2rem;text-align:center">Planetarium – it’s live 🌌</h1>
HTML
  else
    for f in "${LOOSE_HTML[@]}"; do
      base="$(basename "$f")"
      name="${base%.*}"
      safe="$(echo "$name" | tr '[:upper:] ' '[:lower:]-' | sed 's/[^a-z0-9-]//g')"
      APP_PATH="$APPS_DIR/$safe/public"
      mkdir -p "$APP_PATH"
      cp -f "$f" "$APP_PATH/index.html"
      echo_success "Created app '$safe' from $f"
    done
  fi
fi

# ---------- Ensure vercel.json for static sites ----------
while IFS= read -r -d '' D; do
  APP_NAME="$(basename "$D")"
  if [ ! -f "$D/vercel.json" ] && [ -d "$D/public" ]; then
    cat > "$D/vercel.json" <<'JSON'
{
  "version": 2,
  "builds": [{ "src": "public/**", "use": "@vercel/static" }],
  "routes": [{ "src": "/(.*)", "dest": "/public/$1" }]
}
JSON
    echo_success "vercel.json created for $APP_NAME (static)."
  fi
done < <(find "$APPS_DIR" -mindepth 1 -maxdepth 1 -type d -print0)

# ---------- Link each app to Vercel ----------
upper_key() { basename "$1" | tr '[:lower:]-' '[:upper:]_' | sed 's/[^A-Z0-9_]/_/g'; }

echo_info "Linking apps to Vercel…"
mapfile -t APP_DIRS < <(find "$APPS_DIR" -mindepth 1 -maxdepth 1 -type d | sort)
[ ${#APP_DIRS[@]} -gt 0 ] || { echo_error "No apps under $APPS_DIR"; exit 1; }

for APP in "${APP_DIRS[@]}"; do
  APP_NAME="$(basename "$APP")"
  PJ="$APP/.vercel/project.json"
  if [ ! -f "$PJ" ]; then
    echo_info "Linking '$APP_NAME'…"
    if [ -n "$VERCEL_SCOPE" ]; then
      vercel link --yes --project "$APP_NAME" --scope "$VERCEL_SCOPE" --cwd "$APP" || true
    else
      vercel link --yes --project "$APP_NAME" --cwd "$APP" || true
    fi
  fi
  if [ ! -f "$PJ" ]; then
    echo_warn "App '$APP_NAME' not linked (project may not exist). Open Vercel UI for '$APP_NAME' once, or set VERCEL_SCOPE and re-run."
  else
    echo_success "'$APP_NAME' is linked."
  fi
done

# ---------- Collect org/project IDs & build Actions matrix ----------
MATRIX=""
ORG_ID_GLOBAL=""
SECRETS_EXPORTS=""
for APP in "${APP_DIRS[@]}"; do
  APP_NAME="$(basename "$APP")"
  KEY="$(upper_key "$APP_NAME")"
  PJ="$APP/.vercel/project.json"
  if [ ! -f "$PJ" ]; then
    echo_warn "Skipping '$APP_NAME' (no .vercel/project.json)."
    continue
  fi
  ORG_ID="$(jq -r '.orgId // empty' "$PJ")"
  PROJECT_ID="$(jq -r '.projectId // empty' "$PJ")"
  if [ -z "$ORG_ID" ] || [ -z "$PROJECT_ID" ]; then
    echo_warn "Skipping '$APP_NAME' (missing orgId/projectId)."
    continue
  fi
  [ -z "$ORG_ID_GLOBAL" ] && ORG_ID_GLOBAL="$ORG_ID"

  read -r -d '' ITEM <<JSON || true
          - name: $APP_NAME
            cwd: apps/$APP_NAME
            project_key: $KEY
JSON
  MATRIX+="$ITEM"$'\n'
  SECRETS_EXPORTS+="VERCEL_PROJECT_ID_${KEY}=$PROJECT_ID"$'\n'
done

[ -n "$MATRIX" ] || { echo_error "No linked apps produced a matrix."; exit 1; }

cat > "$WF_FILE" <<'YML'
name: Deploy web apps to Vercel
on:
  push: { branches: [ main, master ] }
  workflow_dispatch: {}
jobs:
  deploy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app:
YML

# append the matrix items safely
printf "%s\n" "$MATRIX" >> "$WF_FILE"

cat >> "$WF_FILE" <<'YML'
    defaults:
      run:
        working-directory: ${{ matrix.app.cwd }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Install Vercel CLI
        run: npm i -g vercel@latest
      - name: Pull env (Vercel)
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets['VERCEL_PROJECT_ID_' + matrix.app.project_key] }}
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: vercel pull --yes --environment=production
      - name: Build
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: vercel build --prod
      - name: Deploy (prebuilt)
        id: deploy
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          url=$(vercel deploy --prebuilt --prod)
          echo "url=$url" >> $GITHUB_OUTPUT
      - name: Output URL
        run: echo "✅ Deployed ${{ matrix.app.name }} → ${{ steps.deploy.outputs.url }}"
YML

echo_success "Matrix workflow written: $WF_FILE"

# ---------- Print required secrets ----------
echo
echo "────────────────────────────────────"
echo "🔐 REQUIRED GITHUB ACTIONS SECRETS"
echo "Add in: Repo → Settings → Secrets and variables → Actions"
echo
echo "VERCEL_TOKEN   = <your vercel token>"
[ -n "$ORG_ID_GLOBAL" ] && echo "VERCEL_ORG_ID  = $ORG_ID_GLOBAL"
printf "%s" "$SECRETS_EXPORTS" | sed 's/^/ /'
echo "────────────────────────────────────"
echo

# ---------- Optional: push secrets via gh ----------
if [ ${GH_OK} -eq 1 ] && git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  cd "$REPO_ROOT"
  if [ -n "${VERCEL_TOKEN:-}" ]; then
    printf "%s" "$VERCEL_TOKEN" | gh secret set VERCEL_TOKEN --app actions
  else
    echo_warn "export VERCEL_TOKEN=xxxxx then re-run to auto-upload it."
  fi
  [ -n "$ORG_ID_GLOBAL" ] && printf "%s" "$ORG_ID_GLOBAL" | gh secret set VERCEL_ORG_ID --app actions
  while IFS='=' read -r K V; do
    [ -z "$K" ] && continue
    printf "%s" "$V" | gh secret set "$K" --app actions
  done <<< "$SECRETS_EXPORTS"
  echo_success "Pushed secrets via gh."
else
  echo_info "Skipping automatic secret upload (gh not available or repo not detected)."
fi

echo_success "All apps processed."
