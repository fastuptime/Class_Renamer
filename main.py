#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import shutil
import random
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class SafeClassRenamer:
    def __init__(self, project_dir: str = None):
        self.project_dir = project_dir or os.path.dirname(os.path.abspath(__file__))
        self.backup_dir = os.path.join(self.project_dir, f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        self.class_mappings = {}
        self.stats = {
            'html_files': 0,
            'css_files': 0,
            'classes_found': 0,
            'classes_renamed': 0,
            'files_updated': 0
        }
        self.name_counter = 0

    def extract_classes_from_html(self, file_path: str) -> Set[str]:
        classes = set()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            pattern = r'class\s*=\s*["\']([^"\']+)["\']'
            matches = re.findall(pattern, content, re.IGNORECASE)

            for match in matches:
                class_names = match.strip().split()
                for class_name in class_names:
                    class_name = class_name.strip()
                    if re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', class_name):
                        classes.add(class_name)

        except Exception as e:
            print(f"⚠️ HTML read error {file_path}: {e}")

        return classes

    def extract_classes_from_css(self, file_path: str) -> Set[str]:
        classes = set()
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

            content = self.filter_problematic_css_areas(content)

            pattern = r'\.([a-zA-Z][a-zA-Z0-9_-]*)'
            matches = re.findall(pattern, content)

            for match in matches:
                if not self.is_problematic_class_name(match):
                    classes.add(match)

        except Exception as e:
            print(f"⚠️ CSS read error {file_path}: {e}")

        return classes

    def filter_problematic_css_areas(self, content: str) -> str:
        content = re.sub(r'@keyframes\s+[^{]+\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', '', content, flags=re.DOTALL)
        content = re.sub(r':root\s*\{[^}]*\}', '', content, flags=re.DOTALL)
        content = re.sub(r'calc\([^)]+\)', '', content)
        content = re.sub(r'url\([^)]+\)', '', content)
        content = re.sub(r'["\'][^"\']*["\']', '', content)
        return content

    def is_problematic_class_name(self, class_name: str) -> bool:
        css_keywords = {'inherit', 'initial', 'unset', 'none', 'auto', 'normal', 'default',
                        'left', 'right', 'center', 'top', 'bottom', 'middle', 'block',
                        'inline', 'flex', 'grid', 'table', 'absolute', 'relative', 'fixed',
                        'sticky', 'static', 'hidden', 'visible', 'scroll', 'contain', 'cover'}
        css_units = {'px', 'em', 'rem', 'vh', 'vw', 'pt', 'pc', 'in', 'cm', 'mm', 's', 'ms'}
        color_names = {'red', 'blue', 'green', 'yellow', 'black', 'white', 'gray', 'grey',
                       'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta'}
        
        if len(class_name) <= 2:
            return True
        if class_name.lower() in css_keywords or class_name.lower() in css_units or class_name.lower() in color_names:
            return True
        if class_name.isdigit():
            return True
        return False
        
    def analyze_all_classes(self) -> Dict[str, List[str]]:
        print("🔍 Class'lar analiz ediliyor...")
        all_classes = defaultdict(list)
        
        for root, dirs, files in os.walk(self.project_dir):
            if 'backup_' in root or 'node_modules' in root or '.git' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                if file.lower().endswith(('.html', '.htm')):
                    self.stats['html_files'] += 1
                    classes = self.extract_classes_from_html(file_path)
                    for class_name in classes:
                        all_classes[class_name].append(f"HTML: {os.path.relpath(file_path, self.project_dir)}")
                elif file.lower().endswith('.css'):
                    self.stats['css_files'] += 1
                    classes = self.extract_classes_from_css(file_path)
                    for class_name in classes:
                        all_classes[class_name].append(f"CSS: {os.path.relpath(file_path, self.project_dir)}")
        
        self.stats['classes_found'] = len(all_classes)
        return dict(all_classes)

    def generate_sequential_name(self) -> str:
        new_name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6))
        self.name_counter += 1
        return new_name

    def create_mappings(self, all_classes: Dict[str, List[str]]) -> Dict[str, str]:
        print(" Class mapping'leri oluşturuluyor...")
        
        mappings = {}
        for old_name in sorted(all_classes.keys()):
            if not self.is_problematic_class_name(old_name) and len(old_name) > 3:
                 new_name = self.generate_sequential_name()
                 mappings[old_name] = new_name
            else:
                mappings[old_name] = old_name
        
        self.stats['classes_renamed'] = len([old for old, new in mappings.items() if old != new])
        return mappings

    def create_backup(self, file_path: str):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        rel_path = os.path.relpath(file_path, self.project_dir)
        backup_path = os.path.join(self.backup_dir, rel_path)
        
        backup_dir = os.path.dirname(backup_path)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        shutil.copy2(file_path, backup_path)
    
    def update_html_file(self, file_path: str) -> int:
        try:
            self.create_backup(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            updates_count = 0
            
            def replace_class_attribute(match):
                nonlocal updates_count
                quote_char = match.group(1)
                class_value = match.group(2)
                
                classes = class_value.strip().split()
                updated_classes = []
                
                for class_name in classes:
                    if class_name in self.class_mappings and self.class_mappings[class_name] != class_name:
                        updated_classes.append(self.class_mappings[class_name])
                        updates_count += 1
                    else:
                        updated_classes.append(class_name)
                
                return f'class={quote_char}{" ".join(updated_classes)}{quote_char}'
            
            pattern = r'class\s*=\s*(["\'])([^"\']*?)\1'
            content = re.sub(pattern, replace_class_attribute, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return updates_count
            
            return 0
        
        except Exception as e:
            print(f" HTML güncelleme hatası {file_path}: {e}")
            self.restore_from_backup(file_path)
            return 0
    
    def update_css_file(self, file_path: str) -> int:
        try:
            self.create_backup(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            updates_count = 0
            
            if not self.is_valid_css_structure(content):
                print(f"⚠️ CSS yapısı problemli, güncelleme atlanıyor: {os.path.basename(file_path)}")
                return 0
            
            for old_class, new_class in self.class_mappings.items():
                if old_class == new_class:
                    continue
                
                escaped_old = re.escape(old_class)
                
                patterns = [
                    rf'(?<![a-zA-Z0-9_-])\.{escaped_old}(?=\s*[\{{,])',
                    rf'(?<![a-zA-Z0-9_-])\.{escaped_old}(?=\s*[\{{,\s])',
                ]
                
                for pattern in patterns:
                    old_content = content
                    content = re.sub(pattern, f'.{new_class}', content)
                    if old_content != content:
                        updates_count += 1
            
            if not self.is_valid_css_structure(content):
                print(f"⚠️ Güncelleme sonrası CSS bozuldu, geri alınıyor: {os.path.basename(file_path)}")
                self.restore_from_backup(file_path)
                return 0
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return updates_count
            
            return 0
        
        except Exception as e:
            print(f" CSS güncelleme hatası {file_path}: {e}")
            self.restore_from_backup(file_path)
            return 0

    def is_valid_css_structure(self, content: str) -> bool:
        if not content.strip():
            return True
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            return False
        has_css_rules = bool(re.search(r'[^{}]+\s*\{[^{}]*\}', content, re.DOTALL))
        has_at_rules = bool(re.search(r'@[a-zA-Z-]+', content))
        has_comments = bool(re.search(r'/\*.*?\*/', content, re.DOTALL))
        return has_css_rules or has_at_rules or has_comments
    
    def restore_from_backup(self, file_path: str):
        try:
            rel_path = os.path.relpath(file_path, self.project_dir)
            backup_file = os.path.join(self.backup_dir, rel_path)
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, file_path)
                print(f"   Backup'tan geri yüklendi: {os.path.basename(file_path)}")
            else:
                print(f"   Backup bulunamadı: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"   Geri yükleme hatası: {e}")
    
    def read_file_safely(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except:
            return ""

    def update_all_files(self):
        print(" Dosyalar güncelleniyor...")
        total_updates = 0
        
        for root, dirs, files in os.walk(self.project_dir):
            if 'backup_' in root or 'node_modules' in root or '.git' in root:
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                updates_count = 0
                
                if file.lower().endswith(('.html', '.htm')):
                    updates_count = self.update_html_file(file_path)
                elif file.lower().endswith('.css'):
                    updates_count = self.update_css_file(file_path)
                
                if updates_count > 0:
                    rel_path = os.path.relpath(file_path, self.project_dir)
                    print(f"   {rel_path}: {updates_count} class güncellendi")
                    total_updates += updates_count
                    self.stats['files_updated'] += 1
        return total_updates
        
    def save_mapping_report(self, all_classes: Dict[str, List[str]]):
        report = {
            'meta': {
                'project_dir': self.project_dir,
                'backup_dir': self.backup_dir,
                'date': datetime.now().isoformat(),
                'stats': self.stats
            },
            'mappings': self.class_mappings,
            'class_usage': all_classes
        }
        
        report_file = os.path.join(self.project_dir, 'class_rename_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f" Mapping raporu kaydedildi: {os.path.basename(report_file)}")
    
    def run(self):
        print("X Class Renamer Başlatılıyor...")
        print(f" Proje Dizini: {self.project_dir}")
        
        all_classes = self.analyze_all_classes()
        
        if not all_classes:
            print(" Hiç class bulunamadı!")
            return
        
        print(f"📊 Bulunan: {self.stats['html_files']} HTML, {self.stats['css_files']} CSS dosyası")
        print(f"🔍 Toplam {self.stats['classes_found']} benzersiz class bulundu")
        
        self.class_mappings = self.create_mappings(all_classes)
        
        renamed_count = sum(1 for old, new in self.class_mappings.items() if old != new)
        
        if not self.class_mappings or renamed_count == 0:
            print("ℹ️ Yeniden adlandırılacak class yok - tüm class isimleri zaten düzgün!")
            return
        
        self.stats['classes_renamed'] = renamed_count
        print(f" {renamed_count} class yeniden adlandırılacak")
        
        print(f"\n📋 Örnek Mapping'ler:")
        example_count = 0
        for old, new in self.class_mappings.items():
            if old != new:
                print(f"  {old} → {new}")
                example_count += 1
            if example_count >= 5:
                break
        
        if renamed_count > 5:
            print(f"  ... ve {renamed_count - 5} tane daha")
        
        print(f"\n Backup dizini: {self.backup_dir}")
        response = input("\n Devam etmek istiyor musunuz? (y/N): ").strip().lower()
        
        if response not in ['y', 'yes', 'evet', 'e']:
            print(" İşlem iptal edildi")
            return
        
        print("\n Dosyalar güncelleniyor...")
        total_updates = self.update_all_files()
        
        self.save_mapping_report(all_classes)
        
        print(f"\n İşlem Tamamlandı!")
        print(f" Özet:")
        print(f"   İşlenen HTML dosyası: {self.stats['html_files']}")
        print(f"   İşlenen CSS dosyası: {self.stats['css_files']}")
        print(f"   Bulunan toplam class: {self.stats['classes_found']}")
        print(f"   Yeniden adlandırılan class: {self.stats['classes_renamed']}")
        print(f"   Güncellenen dosya: {self.stats['files_updated']}")
        print(f"  Toplam güncelleme: {total_updates}")
        print(f"\n Backup Dizini: {self.backup_dir}")
        print(f" Sorun yaşanırsa backup'tan geri yükleyebilirsiniz")
    
    def rollback(self, backup_dir: str = None):
        backup_path = backup_dir or self.backup_dir
        
        if not os.path.exists(backup_path):
            print(f" Backup dizini bulunamadı: {backup_path}")
            return
        
        print(f" Geri yükleme başlatılıyor: {backup_path}")
        restored_count = 0
        
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                backup_file = os.path.join(root, file)
                rel_path = os.path.relpath(backup_file, backup_path)
                original_file = os.path.join(self.project_dir, rel_path)
                
                try:
                    os.makedirs(os.path.dirname(original_file), exist_ok=True)
                    shutil.copy2(backup_file, original_file)
                    restored_count += 1
                    print(f"   Geri yüklendi: {rel_path}")
                except Exception as e:
                    print(f"   Geri yükleme hatası {rel_path}: {e}")
        
        print(f" Geri yükleme tamamlandı! {restored_count} dosya geri yüklendi")

def main():
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'rollback':
            if len(sys.argv) > 2:
                backup_dir = sys.argv[2]
                renamer = SafeClassRenamer()
                renamer.rollback(backup_dir)
            else:
                print(" Kullanım: python class_renamer.py rollback <backup_dizini>")
            return
    
    renamer = SafeClassRenamer()
    renamer.run()

if __name__ == "__main__":
    main()
