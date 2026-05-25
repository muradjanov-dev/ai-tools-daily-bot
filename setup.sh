#!/bin/bash
# AI Tools Bot - Avtomatik sozlash
# Foydalanish: bash setup.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🤖 AI Tools Bot - Avto Sozlash    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
echo ""

# 1. gh CLI tekshirish
if ! command -v gh &> /dev/null; then
    echo -e "${RED}❌ gh (GitHub CLI) o'rnatilmagan${NC}"
    echo -e "${YELLOW}O'rnatish:${NC}"
    echo "  macOS:   brew install gh"
    echo "  Linux:   sudo apt install gh"
    echo "  Windows: winget install GitHub.cli"
    exit 1
fi

# 2. GitHub auth
echo -e "${YELLOW}🔐 GitHub ga kirish tekshirilmoqda...${NC}"
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}GitHub ga kiring:${NC}"
    gh auth login
fi
echo -e "${GREEN}✅ GitHub auth OK${NC}"

# 3. Anthropic API key
echo ""
echo -e "${YELLOW}🔑 Anthropic API key kiriting:${NC}"
echo -e "${BLUE}   (olish: https://console.anthropic.com/settings/keys)${NC}"
read -s -p "API Key: " ANTHROPIC_KEY
echo ""

if [[ -z "$ANTHROPIC_KEY" ]]; then
    echo -e "${RED}❌ API key bo'sh!${NC}"
    exit 1
fi

# 4. Repository yaratish
REPO_NAME="ai-tools-daily-bot"
echo ""
echo -e "${YELLOW}📦 GitHub repository yaratilmoqda: $REPO_NAME${NC}"

if gh repo view "$REPO_NAME" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Repository allaqachon mavjud${NC}"
    read -p "Davom etamizmi? (y/n): " CONTINUE
    if [[ "$CONTINUE" != "y" ]]; then
        exit 0
    fi
else
    gh repo create "$REPO_NAME" --private --description "🤖 AI Tools Daily - Uzbek Telegram Bot"
    echo -e "${GREEN}✅ Repository yaratildi${NC}"
fi

# 5. Git remote sozlash
GITHUB_USER=$(gh api user --jq .login)
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

if git remote get-url origin &> /dev/null; then
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi

# 6. Push
echo ""
echo -e "${YELLOW}📤 Kod push qilinmoqda...${NC}"
git branch -M main
git push -u origin main --force
echo -e "${GREEN}✅ Kod yuklandi${NC}"

# 7. Secrets qo'shish
echo ""
echo -e "${YELLOW}🔒 Secrets qo'shilmoqda...${NC}"

gh secret set TELEGRAM_BOT_TOKEN --body "8973818061:AAFHtTUOYMcW_Qpp5e--giI8km1EN_oBicg" --repo "$GITHUB_USER/$REPO_NAME"
gh secret set TELEGRAM_CHANNEL_ID --body "-1001161187842" --repo "$GITHUB_USER/$REPO_NAME"
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_KEY" --repo "$GITHUB_USER/$REPO_NAME"

echo -e "${GREEN}✅ Hamma secret qo'shildi${NC}"

# 8. Workflow ishga tushirish
echo ""
echo -e "${YELLOW}🚀 Birinchi xabar yuborish testi...${NC}"
sleep 2
gh workflow run "daily_ai_tools.yml" --repo "$GITHUB_USER/$REPO_NAME"
echo -e "${GREEN}✅ Workflow ishga tushdi${NC}"

# 9. Yakuniy ma'lumot
echo ""
echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       🎉 BARCHASI TAYYOR! 🎉        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "📍 ${BLUE}Repository:${NC} https://github.com/$GITHUB_USER/$REPO_NAME"
echo -e "⚡ ${BLUE}Workflow:${NC}   https://github.com/$GITHUB_USER/$REPO_NAME/actions"
echo ""
echo -e "🕐 ${YELLOW}Bot har kuni soat 09:00 (Toshkent) da ishga tushadi${NC}"
echo -e "📱 ${YELLOW}1-2 daqiqada birinchi test xabar kanalingizga keladi${NC}"
echo ""
echo -e "${BLUE}🤖 Bot tinch ishlaydi — siz uxlasangiz ham xabarlar yuboriladi!${NC}"
