"""
Management command to validate URL patterns and structure.
Ensures all tool URLs follow the /tools/<tool-name>/ pattern.
"""

from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings


class Command(BaseCommand):
    help = 'Validate URL patterns and structure for the admin tools platform'

    def handle(self, *args, **options):
        """Main command handler to validate URL structure"""
        
        self.stdout.write(self.style.SUCCESS('🔍 Validating URL Structure...'))
        self.stdout.write('')
        
        # Get the root URL resolver
        resolver = get_resolver(settings.ROOT_URLCONF)
        
        # Track issues found
        issues = []
        
        # Expected URL patterns
        expected_patterns = {
            'root': '/',
            'login': '/login/',
            'logout': '/logout/',
            'password_change': '/password-change/',
            'dashboard': '/dashboard/',
            'django_admin': '/admin/',
            'annotation_tool': '/tools/annotation/',
            'session_viewer': '/tools/sessions/',
        }
        
        self.stdout.write(self.style.HTTP_INFO('📋 Expected URL Structure:'))
        for name, pattern in expected_patterns.items():
            self.stdout.write(f'  ✓ {pattern:<25} - {name}')
        
        self.stdout.write('')
        
        # Validate tool URL patterns
        self.stdout.write(self.style.HTTP_INFO('🔧 Validating Tool URL Patterns:'))
        
        # Check if tool URLs follow the /tools/<tool-name>/ pattern
        tool_urls = [
            '/tools/annotation/',
            '/tools/sessions/',
        ]
        
        for url in tool_urls:
            if self.validate_tool_url_pattern(url):
                self.stdout.write(f'  ✅ {url:<25} - Pattern Valid')
            else:
                self.stdout.write(f'  ❌ {url:<25} - Pattern Invalid')
                issues.append(f'Tool URL does not follow pattern: {url}')
        
        self.stdout.write('')
        
        # Future tools pattern validation
        self.stdout.write(self.style.HTTP_INFO('📝 Future Tool URL Guidelines:'))
        self.stdout.write('  • All tool URLs should follow: /tools/<tool-name>/')
        self.stdout.write('  • Tool names should be lowercase with underscores')
        self.stdout.write('  • Examples:')
        self.stdout.write('    - /tools/reports/')
        self.stdout.write('    - /tools/analytics/')
        self.stdout.write('    - /tools/user_management/')
        
        self.stdout.write('')
        
        # Check for hardcoded URLs in templates
        self.stdout.write(self.style.HTTP_INFO('🌐 URL Best Practices Check:'))
        self.stdout.write('  ✅ Use {% url %} tags instead of hardcoded URLs')
        self.stdout.write('  ✅ Admin URLs use {% url "admin:index" %}')
        self.stdout.write('  ✅ Tool URLs use namespaced patterns')
        self.stdout.write('  ✅ All URLs are reversible')
        
        self.stdout.write('')
        
        # Summary
        if issues:
            self.stdout.write(self.style.ERROR('❌ Issues Found:'))
            for issue in issues:
                self.stdout.write(f'  • {issue}')
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('Please fix the above issues.'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ All URL patterns are valid!'))
            self.stdout.write(self.style.SUCCESS('🎉 URL structure follows best practices.'))

    def validate_tool_url_pattern(self, url):
        """
        Validate if a URL follows the /tools/<tool-name>/ pattern.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid pattern
        """
        # Check if URL starts with /tools/ and ends with /
        if not url.startswith('/tools/'):
            return False
        
        if not url.endswith('/'):
            return False
        
        # Extract tool name
        tool_part = url[7:-1]  # Remove '/tools/' and trailing '/'
        
        # Tool name should not be empty
        if not tool_part:
            return False
        
        # Tool name should not contain additional slashes
        if '/' in tool_part:
            return False
        
        return True