@echo off
chcp 65001 >nul
REM ============================================================================
REM ISAC 文献综述自动化系统 — Windows 一键启动脚本
REM ============================================================================
REM 使用方法：
REM   1. 双击此文件运行
REM   2. 或在命令行中: run_weekly.bat
REM   3. 或带参数:  run_weekly.bat --test
REM               run_weekly.bat --skip-fetch
REM               run_weekly.bat --max 100
REM ============================================================================

cd /d "%~dp0"

echo =====================================================
echo   ISAC 文献综述自动化系统
echo   面向6G的通信感知一体化 (ISAC)
echo =====================================================
echo.

REM 检查 Python 是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请确保 Python 已安装并在 PATH 中
    pause
    exit /b 1
)

python --version
echo.

REM 检查依赖是否安装
python -c "import arxiv, sklearn, numpy, pandas, nltk" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 部分依赖包缺失，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败，请手动执行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM 传递所有参数给主控脚本
echo [启动] 运行流水线...
python run_pipeline.py %*

echo.
echo =====================================================
echo   完成！请查看 data/ 目录中的输出文件
echo =====================================================
echo.
echo   输出文件：
echo     - data\papers_raw.json       原始论文数据
echo     - data\paper_cards.jsonl     论文卡片
echo     - data\taxonomy.md           研究分类法
echo     - data\comparison_table.csv  方法对比表
echo     - data\weekly_digest.md      周度综述
echo.

pause
