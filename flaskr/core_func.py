import os, yaml



def create_footer_urls():
    """
    This function will read the YAML file called footer_links.yaml in the 
    lab section and create the HTML links at the bottom bar from that data.
    """
    yaml_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir, 'flaskr/yaml/footer_links.yaml'))
    if os.path.exists(yaml_path):
        print("The footers yaml file exists, procesing")
        yaml_data = open(yaml_path, 'r')
        list_of_urls = yaml.load(yaml_data, Loader=yaml.FullLoader)
    else:
        print("Couldn't find the footer YAML file. Returning empty!")
        print("!!!!!!!! -> "+yaml_path)
        list_of_urls=[]
    return list_of_urls
