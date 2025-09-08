"""
Management command to set up tool permissions for users.
Provides an easy way to assign users to tool groups.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from core.permissions import assign_user_to_tool

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up tool permissions for users'

    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--user',
            type=str,
            help='Username to assign permissions to'
        )
        parser.add_argument(
            '--tool',
            type=str,
            choices=['annotation', 'session_viewer', 'all'],
            help='Tool to grant access to (annotation, session_viewer, or all)'
        )
        parser.add_argument(
            '--list-groups',
            action='store_true',
            help='List all available tool groups'
        )
        parser.add_argument(
            '--superuser-all',
            action='store_true',
            help='Grant all permissions to all superusers'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        
        # List groups option
        if options['list_groups']:
            self.list_tool_groups()
            return
        
        # Grant all permissions to superusers
        if options['superuser_all']:
            self.grant_superuser_permissions()
            return
        
        # Require both user and tool for individual assignment
        if not options['user'] or not options['tool']:
            self.stdout.write(
                self.style.ERROR(
                    'Please specify both --user and --tool, or use --list-groups or --superuser-all'
                )
            )
            return
        
        # Assign user to tool
        self.assign_user_permission(options['user'], options['tool'])

    def list_tool_groups(self):
        """List all available tool groups and their members"""
        self.stdout.write(self.style.SUCCESS('Available Tool Groups:'))
        
        groups = Group.objects.filter(name__in=['annotation_users', 'session_viewers'])
        for group in groups:
            self.stdout.write(f"\n  • {group.name}")
            users = group.user_set.all()
            if users:
                for user in users:
                    status = "(superuser)" if user.is_superuser else ""
                    self.stdout.write(f"    - {user.username} {status}")
            else:
                self.stdout.write("    - No users assigned")

    def grant_superuser_permissions(self):
        """Grant all tool permissions to all superusers"""
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers:
            self.stdout.write(self.style.WARNING('No superusers found.'))
            return
        
        annotation_group = Group.objects.get(name='annotation_users')
        session_group = Group.objects.get(name='session_viewers')
        
        for user in superusers:
            user.groups.add(annotation_group, session_group)
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Granted all tool permissions to superuser: {user.username}'
                )
            )

    def assign_user_permission(self, username, tool):
        """Assign a specific user permission for a tool"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found.')
            )
            return
        
        if tool == 'all':
            # Assign to both groups
            success_annotation = assign_user_to_tool(user, 'annotation')
            success_session = assign_user_to_tool(user, 'session_viewer')
            
            if success_annotation and success_session:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Granted all tool permissions to user: {username}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error granting permissions to user: {username}'
                    )
                )
        else:
            # Assign to specific tool
            success = assign_user_to_tool(user, tool)
            
            if success:
                tool_display = tool.replace('_', ' ').title()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Granted {tool_display} permission to user: {username}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error granting {tool} permission to user: {username}'
                    )
                )