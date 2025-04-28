import os
import json

def update_gateway_version_subdirectory(root_dir, new_version):
    """
    Updates the @apollo/gateway version in package.json files found directly in subdirectories
    of the root directory.

    Args:
        root_dir (str): The root directory to search within.
        new_version (str): The new version string for @apollo/gateway (e.g., "2.10.0").
    """
    updated_count = 0
    subdirectories = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]

    for subdir_name in subdirectories:
        filepath = os.path.join(root_dir, subdir_name, "package.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)

                if "dependencies" in data and "@apollo/gateway" in data["dependencies"]:
                    old_version = data["dependencies"]["@apollo/gateway"]
                    data["dependencies"]["@apollo/gateway"] = new_version
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"Updated @apollo/gateway from {old_version} to {new_version} in: {filepath}")
                    updated_count += 1
                elif "devDependencies" in data and "@apollo/gateway" in data["devDependencies"]:
                    old_version = data["devDependencies"]["@apollo/gateway"]
                    data["devDependencies"]["@apollo/gateway"] = new_version
                    with open(filepath, 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"Updated @apollo/gateway from {old_version} to {new_version} in: {filepath}")
                    updated_count += 1
                else:
                    print(f"@apollo/gateway not found in dependencies or devDependencies in: {filepath}")

            except FileNotFoundError:
                print(f"Error: package.json not found at: {filepath}")
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON in: {filepath}")
            except Exception as e:
                print(f"An unexpected error occurred with {filepath}: {e}")
        else:
            print(f"package.json not found in subdirectory: {os.path.join(root_dir, subdir_name)}")

    print(f"\nSuccessfully updated @apollo/gateway in {updated_count} package.json files within the first level of subdirectories.")

if __name__ == "__main__":
    root_directory = input("Enter the root directory containing the subdirectories: ")
    new_gateway_version = "2.10.0"
    update_gateway_version_subdirectory(root_directory, new_gateway_version)
