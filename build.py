import os
import sys
import shutil
from PyInstaller.config import CONF
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

def build_app():
    # 初始化PyInstaller配置
    CONF['workpath'] = os.path.join(os.getcwd(), 'build')
    CONF['distpath'] = os.path.join(os.getcwd(), 'dist')
    CONF['specpath'] = os.getcwd()
    CONF['spec'] = os.path.join(os.getcwd(), '智能背单词.spec')
    CONF['warnfile'] = os.path.join(os.getcwd(), 'build', 'warn-智能背单词.txt')
    CONF['noconfirm'] = False
    CONF['code_cache'] = {}
    CONF['xref-file'] = os.path.join(os.getcwd(), 'build', 'xref-智能背单词.txt')
    CONF['upx_available'] = False
    
    # 清理之前的构建
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 确保build目录存在
    os.makedirs('build', exist_ok=True)
        
    # 分析主程序
    a = Analysis(['src/main.py'],
                pathex=['.'],
                binaries=[],
                datas=[],
                hiddenimports=[],
                hookspath=[],
                runtime_hooks=[],
                excludes=[],
                win_no_prefer_redirects=False,
                win_private_assemblies=False,
                cipher=None,
                noarchive=False)
    
    # 创建PYZ文件
    pyz = PYZ(a.pure, a.zipped_data, cipher=None)
    
    # 创建EXE文件
    exe = EXE(pyz,
             a.scripts,
             a.binaries,
             a.zipfiles,
             a.datas,
             [],
             name='智能背单词',
             debug=False,
             bootloader_ignore_signals=False,
             strip=False,
             upx=True,
             upx_exclude=[],
             runtime_tmpdir=None,
             console=False,
             icon=None)

if __name__ == '__main__':
    build_app()
