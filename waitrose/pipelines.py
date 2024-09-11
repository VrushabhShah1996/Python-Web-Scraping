# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymysql import IntegrityError

import waitrose.db_config as db
from waitrose.items import WaitroseItem, WaitroselinkItem


# class SpiritsScraperPipeline:
class WaitrosePipeline:
    data_insert = 0
    variation_insert = 0

    def open_spider(self, spider):

        try:

            create_database = f"CREATE DATABASE IF NOT EXISTS {db.db_name};"
            spider.cursor.execute(create_database)
            spider.cursor.execute(f"USE {db.db_name};")
        except Exception as e:
            spider.logger.info(e)

        try:

            create_table = f"""CREATE TABLE IF NOT EXISTS `{db.db_data_table}` (`Id` INT NOT NULL AUTO_INCREMENT,
                                                                             `htmlpath` varchar(100) DEFAULT NULL,
                                                                             `Platform_Name` varchar(250) DEFAULT NULL,
                                                                             `Platform_URL` varchar(250) DEFAULT NULL,
                                                                             `Product_id` varchar(20) DEFAULT NULL,
                                                                             `Category_1` varchar(250) DEFAULT NULL,
                                                                             `Category_2` varchar(50) DEFAULT NULL,
                                                                             `Category_3` varchar(250) DEFAULT NULL,
                                                                             `Category_4` varchar(250) DEFAULT NULL,
                                                                             `Category_5` varchar(250) DEFAULT NULL,
                                                                             `Category_6` varchar(250) DEFAULT NULL,
                                                                             `Category_7` varchar(250) DEFAULT NULL,
                                                                             `Category_8` varchar(250) DEFAULT NULL,
                                                                             `Sector` varchar(250) DEFAULT NULL,
                                                                             `SKU_Name` varchar(250) DEFAULT NULL,
                                                                             `Manufacturer` varchar(250) DEFAULT NULL,
                                                                             `Brand` varchar(250) DEFAULT NULL,
                                                                             `Pack_Size` varchar(250) DEFAULT NULL,
                                                                             `Price` varchar(250) DEFAULT NULL,
                                                                             `Promo_Price` varchar(250) DEFAULT NULL,
                                                                             `Price_per_unit` varchar(250) DEFAULT NULL,
                                                                             `Age_of_Whisky` varchar(250) DEFAULT NULL,
                                                                             `Country_of_Origin` varchar(250) DEFAULT NULL,
                                                                             `Distillery` varchar(250) DEFAULT NULL,
                                                                             `Pack_type` varchar(250) DEFAULT NULL,
                                                                             `Tasting_Notes` text,
                                                                             `Image_Urls` text,
                                                                             `ABV` varchar(50) DEFAULT NULL,
                                                                             `scrape_date` varchar(50),   
                                                                             UNIQUE KEY `pid` (`Product_id`),
                                                                             PRIMARY KEY (`Id`)
                                                                           ) ENGINE = InnoDB DEFAULT CHARSET = UTF8MB4"""
            spider.cursor.execute(create_table)
        except Exception as e:
            spider.logger.info(e)

        try:

            create_table = f"""CREATE TABLE IF NOT EXISTS {db.db_links_table} (
                          Id INT NOT NULL AUTO_INCREMENT,
                          Product_URL VARCHAR(255) DEFAULT NULL unique,
                          Category_Id VARCHAR(255) DEFAULT NULL,
                          Status VARCHAR(10) DEFAULT NULL,
                          PRIMARY KEY (Id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4;"""
            spider.cursor.execute(create_table)
        except Exception as e:
            spider.logger.info(e)

    def open_link_spider(self, spider):
        try:

            create_database = f"CREATE DATABASE IF NOT EXISTS {db.db_name};"
            spider.cursor.execute(create_database)
            spider.cursor.execute(f"USE {db.db_name};")
        except Exception as e:
            spider.logger.info(e)

        try:

            create_table = f"""CREATE TABLE IF NOT EXISTS {db.db_links_table} (
                          Id INT NOT NULL AUTO_INCREMENT,
                          Product_URL VARCHAR(255) DEFAULT NULL,
                          Product_id VARCHAR(255) DEFAULT NULL unique,
                          Category_Id VARCHAR(255) DEFAULT NULL,
                          Status VARCHAR(10) DEFAULT NULL,
                          PRIMARY KEY (Id)
                        ) ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4;"""
            spider.cursor.execute(create_table)
        except Exception as e:
            spider.logger.info(e)

    def process_item(self, item, spider):

        if isinstance(item, WaitroseItem):
            try:
                Id = item.pop('Id')
                field_list = []
                value_list = []
                for field in item:
                    field_list.append(str(field))
                    value_list.append('%s')
                fields = ','.join(field_list)
                values = ", ".join(value_list)
                insert_db = f"insert into {db.db_data_table}( " + fields + " ) values ( " + values + " )"
                try:
                    status = "Done"
                    spider.cursor.execute(insert_db, tuple(item.values()))
                    spider.con.commit()
                    self.data_insert += 1
                    spider.logger.info(f'Data Inserted...{self.data_insert}')
                except IntegrityError as e:
                    status = "Duplicate"

                update = f'update {db.db_links_table} set status="{status}" where Id=%s'
                # print(update)
                spider.cursor.execute(update, (Id))
                spider.con.commit()
                spider.logger.info('Done...')
            except Exception as e:
                spider.logger.error(e)

        if isinstance(item, WaitroselinkItem):

            try:
                # Id = item.pop('Id')
                field_list = []
                value_list = []
                for field in item:
                    field_list.append(str(field))
                    value_list.append('%s')
                fields = ','.join(field_list)
                values = ", ".join(value_list)
                insert_db = f"insert into {db.db_name}.{db.db_links_table}( " + fields + " ) values ( " + values + " )"
                try:
                    spider.cursor.execute(insert_db, tuple(item.values()))
                    spider.con.commit()
                    self.data_insert += 1
                    spider.logger.info(f'Data Inserted...{self.data_insert}')
                except IntegrityError as e:
                    spider.logger.error(e)
            except Exception as e:
                spider.logger.error(e)

        return item
