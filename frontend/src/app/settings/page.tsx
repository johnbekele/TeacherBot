'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import AppLayout from '@/components/layout/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { User, Bell, Palette, Shield, Save, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

type Tab = 'profile' | 'preferences' | 'appearance' | 'account';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, loadUser } = useAuthStore();
  const [activeTab, setActiveTab] = useState<Tab>('profile');
  const [saving, setSaving] = useState(false);

  // Profile settings
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');

  // Learning preferences
  const [pacePreference, setPacePreference] = useState('medium');
  const [adhdMode, setAdhdMode] = useState(false);
  const [focusMode, setFocusMode] = useState(false);
  const [breakReminders, setBreakReminders] = useState(true);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setPacePreference(user.settings?.pace_preference || 'medium');
      setAdhdMode(user.settings?.adhd_mode || false);
      setFocusMode(user.settings?.focus_mode || false);
      setBreakReminders(user.settings?.break_reminders !== false);
    }
  }, [user]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      await api.updateProfile({ full_name: fullName });
      await loadUser();
      toast.success('Profile updated successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      await api.updateSettings({
        pace_preference: pacePreference,
        adhd_mode: adhdMode,
        focus_mode: focusMode,
        break_reminders: breakReminders,
      });
      await loadUser();
      toast.success('Preferences saved successfully');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex h-full items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Settings</h1>
          <p className="text-muted-foreground">
            Manage your account settings and preferences
          </p>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="profile" className="space-y-6"
          value={activeTab}
          onValueChange={(value) => setActiveTab(value as Tab)}
        >

          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="profile">
              <User className="w-4 h-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="preferences">
              <Bell className="w-4 h-4 mr-2" />
              Learning
            </TabsTrigger>
            <TabsTrigger value="appearance">
              <Palette className="w-4 h-4 mr-2" />
              Appearance
            </TabsTrigger>
            <TabsTrigger value="account">
              <Shield className="w-4 h-4 mr-2" />
              Account
            </TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Update your personal information
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSaveProfile} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      disabled
                      className="cursor-not-allowed"
                    />
                    <p className="text-xs text-muted-foreground">
                      Email cannot be changed
                    </p>
                  </div>

                  <Button type="submit" disabled={saving}>
                    {saving ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        Save Changes
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Learning Preferences Tab */}
          <TabsContent value="preferences">
            <Card>
              <CardHeader>
                <CardTitle>Learning Preferences</CardTitle>
                <CardDescription>
                  Customize how you learn and interact with content
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSavePreferences} className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="pace">Learning Pace</Label>
                    <Select value={pacePreference} onValueChange={setPacePreference}>
                      <SelectTrigger id="pace">
                        <SelectValue placeholder="Select pace" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="slow">Slow - Take your time</SelectItem>
                        <SelectItem value="medium">Medium - Balanced pace</SelectItem>
                        <SelectItem value="fast">Fast - Quick progression</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      How quickly you want to progress through content
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                      <div className="flex-1 space-y-0.5">
                        <Label htmlFor="adhd-mode" className="text-base font-medium">
                          ADHD-Friendly Mode
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          Extra visual cues, smaller chunks, and more frequent rewards
                        </p>
                      </div>
                      <Switch
                        id="adhd-mode"
                        checked={adhdMode}
                        onCheckedChange={setAdhdMode}
                      />
                    </div>

                    <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                      <div className="flex-1 space-y-0.5">
                        <Label htmlFor="focus-mode" className="text-base font-medium">
                          Focus Mode
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          Hide distractions and show only essential content
                        </p>
                      </div>
                      <Switch
                        id="focus-mode"
                        checked={focusMode}
                        onCheckedChange={setFocusMode}
                      />
                    </div>

                    <div className="flex items-center justify-between space-x-2 rounded-lg border p-4">
                      <div className="flex-1 space-y-0.5">
                        <Label htmlFor="break-reminders" className="text-base font-medium">
                          Break Reminders
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          Get reminded to take breaks every 45 minutes
                        </p>
                      </div>
                      <Switch
                        id="break-reminders"
                        checked={breakReminders}
                        onCheckedChange={setBreakReminders}
                      />
                    </div>
                  </div>

                  <Button type="submit" disabled={saving}>
                    {saving ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="mr-2 h-4 w-4" />
                        Save Preferences
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Appearance Tab */}
          <TabsContent value="appearance">
            <Card>
              <CardHeader>
                <CardTitle>Appearance Settings</CardTitle>
                <CardDescription>
                  Customize the look and feel of your interface
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Theme preferences are managed by the toggle in the header. Your system preference is automatically detected.
                </p>
                <div className="p-4 bg-muted rounded-lg border">
                  <p className="text-sm">
                    Use the moon/sun icon in the top-right corner to toggle between light and dark modes.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Account Tab */}
          <TabsContent value="account">
            <Card>
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
                <CardDescription>
                  Manage your account and security settings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="p-4 bg-destructive/10 rounded-lg border border-destructive/30">
                    <h3 className="font-semibold text-destructive mb-2">
                      Danger Zone
                    </h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Once you sign out, you'll need to log in again to access your account.
                    </p>
                    <Button
                      variant="destructive"
                      onClick={() => {
                        if (confirm('Are you sure you want to sign out?')) {
                          useAuthStore.getState().logout();
                          router.push('/login');
                        }
                      }}
                    >
                      Sign Out
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
}
