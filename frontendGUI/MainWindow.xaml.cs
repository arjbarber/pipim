using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Diagnostics;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Controls;

namespace frontendGUI
{
    public partial class MainWindow : Window
    {
        private readonly HttpClient httpClient = new HttpClient();
        private const string BACKEND_URL = "http://127.0.0.1:5000/";
        private StackPanel viewPackagesContainer;


        public MainWindow()
        {
            InitializeComponent();
            InitializeUI();
        }

        private void InitializeUI()
        {
            Title = "pipim";
            Width = 600;
            Height = 700;
            Background = SystemColors.ControlBrush;

            var tabControl = new TabControl();
            Content = tabControl;

            var viewPackagesTab = new TabItem { Header = "View Installed Packages" };
            var installPackageTab = new TabItem { Header = "Install Package" };
            var searchPackageTab = new TabItem { Header = "Search For Packages" };
            var installPythonTab = new TabItem { Header = "Install Python" };

            viewPackagesTab.Content = CreateViewPackagesUI();
            installPackageTab.Content = CreateInstallPackageUI();
            searchPackageTab.Content = CreateSearchPackageUI();
            installPythonTab.Content = CreateInstallPythonUI();


            tabControl.Items.Add(viewPackagesTab);
            tabControl.Items.Add(installPackageTab);
            tabControl.Items.Add(searchPackageTab);
            tabControl.Items.Add(installPythonTab);
            Debug.WriteLine("hi again");

            
        }

        private ScrollViewer CreateViewPackagesUI()
        {
            viewPackagesContainer = new StackPanel { Margin = new Thickness(10) };
            var scrollViewer = new ScrollViewer { Content = viewPackagesContainer };

            _ = LoadPackagesAsync(viewPackagesContainer);

            return scrollViewer;
        }

        private async void RefreshInstalledPackages()
        {
            if (viewPackagesContainer != null)
            {
                viewPackagesContainer.Children.Clear();
                await LoadPackagesAsync(viewPackagesContainer);
            }
        }

        private async Task LoadPackagesAsync(Panel container)
        {
            try
            {
                // Keep the first child (title), clear everything else
                if (container is StackPanel stack)
                {
                    while (stack.Children.Count > 1)
                        stack.Children.RemoveAt(1);
                }

                var title = new TextBlock { Text = "View Installed Packages", FontSize = 16, Margin = new Thickness(0, 0, 0, 10) };
                viewPackagesContainer.Children.Add(title);

                var response = await httpClient.GetAsync(BACKEND_URL + "get_modules");
                if (response.IsSuccessStatusCode)
                {
                    var data = JsonSerializer.Deserialize<List<Dictionary<string, string>>>(await response.Content.ReadAsStringAsync());

                    foreach (var pkg in data)
                    {
                        string name = pkg["name"];
                        string version = pkg["version"];

                        var infoResp = await httpClient.PostAsync(
                            BACKEND_URL + "get_module_info",
                            new StringContent(JsonSerializer.Serialize(new { package_name = name }), Encoding.UTF8, "application/json")
                        );

                        if (!infoResp.IsSuccessStatusCode) continue;

                        var info = JsonSerializer.Deserialize<Dictionary<string, string>>(await infoResp.Content.ReadAsStringAsync());

                        // Create package container
                        var packagePanel = new StackPanel { Margin = new Thickness(0, 5, 0, 5) };
                        packagePanel.Children.Add(new TextBlock { Text = $"{name} (Version: {version})", FontWeight = FontWeights.Bold });
                        packagePanel.Children.Add(new TextBlock { Text = $"Author: {info["author"]}" });
                        packagePanel.Children.Add(new TextBlock { Text = info["summary"], TextWrapping = TextWrapping.Wrap });

                        var buttonPanel = new StackPanel { Orientation = Orientation.Horizontal };
                        var docButton = new Button { Content = "Documentation", Margin = new Thickness(0, 5, 5, 0) };
                        var removeButton = new Button { Content = "Remove", Margin = new Thickness(0, 5, 5, 0) };

                        docButton.Click += async (s, e) =>
                        {
                            await httpClient.PostAsync(BACKEND_URL + "package_documentation",
                                new StringContent(JsonSerializer.Serialize(new { package_name = name }), Encoding.UTF8, "application/json"));
                        };

                        removeButton.Click += (s, e) => ShowRemovePopup(name);

                        buttonPanel.Children.Add(docButton);
                        buttonPanel.Children.Add(removeButton);

                        packagePanel.Children.Add(buttonPanel);

                        container.Children.Add(packagePanel);
                        container.Children.Add(new Separator());
                    }
                }
                else
                {
                    container.Children.Add(new TextBlock { Text = "No modules installed." });
                }
            }
            catch (Exception ex)
            {
                container.Children.Add(new TextBlock { Text = $"Error: {ex.Message}" });
            }
        }

        private StackPanel CreateInstallPackageUI()
        {
            var panel = new StackPanel { Margin = new Thickness(10) };
            var title = new TextBlock { Text = "Install Package", FontSize = 16, Margin = new Thickness(0, 0, 0, 10) };
            var entry = new TextBox { Width = 200 };
            var button = new Button { Content = "Install", Margin = new Thickness(0, 10, 0, 10) };
            var log = new StackPanel();

            panel.Children.Add(title);
            panel.Children.Add(new TextBlock { Text = "Package Name:" });
            panel.Children.Add(entry);
            panel.Children.Add(button);
            panel.Children.Add(new ScrollViewer { Content = log, Height = 200 });

            button.Click += async (s, e) =>
            {
                var name = entry.Text;
                var content = new StringContent(JsonSerializer.Serialize(new { package_name = name }), Encoding.UTF8, "application/json");
                var resp = await httpClient.PostAsync(BACKEND_URL + "install_package", content);
                var msg = await resp.Content.ReadAsStringAsync();
                var success = resp.IsSuccessStatusCode;
                log.Children.Add(new TextBlock { Text = msg, Foreground = success ? Brushes.Green : Brushes.Red });
            };

            return panel;
        }
                
        private StackPanel CreateSearchPackageUI()
        {
            var panel = new StackPanel { Margin = new Thickness(10) };
            var entry = new TextBox { Width = 200 };
            var button = new Button { Content = "Search", Margin = new Thickness(0, 10, 0, 10) };
            var results = new TextBlock { TextWrapping = TextWrapping.Wrap };

            panel.Children.Add(new TextBlock { Text = "Search For Package", FontSize = 16 });
            panel.Children.Add(new TextBlock { Text = "Package Name:" });
            panel.Children.Add(entry);
            panel.Children.Add(button);
            panel.Children.Add(results);

            button.Click += async (s, e) =>
            {
                var query = entry.Text;
                if (string.IsNullOrWhiteSpace(query))
                {
                    results.Text = "Please enter a package name.";
                    return;
                }

                try
                {
                    var resp = await httpClient.GetAsync(BACKEND_URL + "search_for_packages?q=" + Uri.EscapeDataString(query));
                    if (resp.IsSuccessStatusCode)
                    {
                        var pkgs = JsonSerializer.Deserialize<List<Dictionary<string, string>>>(await resp.Content.ReadAsStringAsync());
                        if (pkgs.Count > 0)
                        {
                            results.Text = string.Join("\n\n", pkgs.ConvertAll(pkg => $"{pkg["name"]} ({pkg["version"]}): {pkg["description"]}"));
                        }
                        else
                        {
                            results.Text = "No packages found.";
                        }
                    }
                    else
                    {
                        results.Text = "Error fetching results.";
                    }
                }
                catch (Exception ex)
                {
                    results.Text = $"Error: {ex.Message}";
                }
            };

            return panel;
        }

        private StackPanel CreateInstallPythonUI()
        {
            var panel = new StackPanel { Margin = new Thickness(10) };
            var button = new Button { Content = "Install Python", Margin = new Thickness(0, 10, 0, 10) };

            panel.Children.Add(new TextBlock { Text = "Install Python", FontSize = 16 });
            panel.Children.Add(button);

            button.Click += async (s, e) =>
            {
                await httpClient.GetAsync(BACKEND_URL + "/install_python");
            };

            return panel;
        }

        private void OpenInstallPythonPopup()
        {
            var popup = new Window
            {
                Title = "Install Python",
                Width = 300,
                Height = 150,
                Background = SystemColors.ControlBrush,
                WindowStartupLocation = WindowStartupLocation.CenterOwner,
                Owner = this
            };

            var closeButton = new Button
            {
                Content = "Close",
                Width = 100,
                HorizontalAlignment = HorizontalAlignment.Center,
                Margin = new Thickness(0, 10, 0, 0)
            };
            closeButton.Click += (s, e) => popup.Close();

            viewPackagesContainer = new StackPanel();
            viewPackagesContainer.Children.Add(new TextBlock
            {
                Text = "Install Python",
                FontSize = 14,
                Margin = new Thickness(0, 20, 0, 10),
                HorizontalAlignment = HorizontalAlignment.Center
            });
            viewPackagesContainer.Children.Add(closeButton);

            popup.Content = viewPackagesContainer;
            popup.ShowDialog();
        }

        private void ShowRemovePopup(string packageName)
        {
            var popup = new Window
            {
                Title = "Remove Package",
                Width = 300,
                Height = 150,
                Background = SystemColors.ControlBrush,
                WindowStartupLocation = WindowStartupLocation.CenterOwner,
                Owner = this
            };

            var confirmButton = new Button
            {
                Content = "Remove",
                Width = 80,
                Margin = new Thickness(5)
            };

            var cancelButton = new Button
            {
                Content = "Cancel",
                Width = 80,
                Margin = new Thickness(5)
            };

            confirmButton.Click += async (s, e) =>
            {
                var content = new StringContent(JsonSerializer.Serialize(new { package_name = packageName }), Encoding.UTF8, "application/json");
                var response = await httpClient.PostAsync(BACKEND_URL + "uninstall_package", content);

                if (response.IsSuccessStatusCode)
                {
                    popup.Close();
                    await Task.Delay(500); // wait a moment to let the backend update
                    RefreshInstalledPackages(); // ✅ refresh the UI
                }
                else
                {
                    MessageBox.Show("Failed to uninstall package.");
                }
            };

            cancelButton.Click += (s, e) => popup.Close();

            var buttons = new StackPanel
            {
                Orientation = Orientation.Horizontal,
                HorizontalAlignment = HorizontalAlignment.Center,
                Children = { confirmButton, cancelButton }
            };

            var contentPanel = new StackPanel
            {
                Margin = new Thickness(10)
            };
            contentPanel.Children.Add(new TextBlock
            {
                Text = $"Are you sure you want to remove {packageName}?",
                TextWrapping = TextWrapping.Wrap
            });
            contentPanel.Children.Add(buttons);

            popup.Content = contentPanel;
            popup.ShowDialog();
        }

    }

    public class RelayCommand : ICommand
    {
        private readonly Action<object> _execute;
        private readonly Func<object, bool> _canExecute;

        public RelayCommand(Action<object> execute, Func<object, bool> canExecute = null)
        {
            _execute = execute;
            _canExecute = canExecute;
        }

        public bool CanExecute(object parameter) => _canExecute?.Invoke(parameter) ?? true;
        public void Execute(object parameter) => _execute(parameter);
        public event EventHandler CanExecuteChanged { add { } remove { } }
    }
}